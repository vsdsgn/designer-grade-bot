import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../wardrobe/domain/clothing_item_model.dart';
import '../../../wardrobe/presentation/providers/wardrobe_provider.dart';
import '../../../tryon/presentation/providers/tryon_provider.dart';
import '../../domain/outfit_model.dart';
import '../providers/outfits_provider.dart';
import '../widgets/outfit_card.dart';

class OutfitsScreen extends ConsumerWidget {
  const OutfitsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final outfitsAsync = ref.watch(outfitsProvider);
    final wardrobeAsync = ref.watch(wardrobeStreamProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Образы'),
        centerTitle: true,
      ),
      body: outfitsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Ошибка: $e')),
        data: (outfits) {
          if (outfits.isEmpty) {
            return const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.bookmark_border, size: 64,
                      color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'Пока нет сохранённых образов',
                    style: TextStyle(color: Colors.grey),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Соберите образ в Примерке и сохраните',
                    style: TextStyle(color: Colors.grey, fontSize: 13),
                  ),
                ],
              ),
            );
          }

          final allItems = wardrobeAsync.valueOrNull ?? [];

          return GridView.builder(
            padding: const EdgeInsets.all(16),
            gridDelegate:
                const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 0.75,
            ),
            itemCount: outfits.length,
            itemBuilder: (context, index) {
              final outfit = outfits[index];
              final urls = outfit.itemIds
                  .map((id) => allItems
                      .where((i) => i.id == id)
                      .map((i) => i.displayUrl)
                      .firstOrNull)
                  .whereType<String>()
                  .toList();

              return OutfitCard(
                outfit: outfit,
                imageUrls: urls,
                onEdit: () => _editOutfit(context, ref, outfit, allItems),
              );
            },
          );
        },
      ),
    );
  }

  void _editOutfit(
    BuildContext context,
    WidgetRef ref,
    OutfitModel outfit,
    List items,
  ) {
    final matchingItems = outfit.itemIds
        .map((id) => items.where((i) => i.id == id).firstOrNull)
        .whereType<ClothingItemModel>()
        .toList();

    ref.read(tryOnSessionProvider.notifier).loadOutfit(matchingItems);
    context.go('/tryon');
  }
}
