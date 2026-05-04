import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/outfit_model.dart';
import '../providers/outfits_provider.dart';
import 'outfit_collage.dart';

class OutfitCard extends ConsumerWidget {
  final OutfitModel outfit;
  final List<String> imageUrls;
  final VoidCallback onEdit;

  const OutfitCard({
    super.key,
    required this.outfit,
    required this.imageUrls,
    required this.onEdit,
  });

  static const _tags = [
    'casual', 'formal', 'sport', 'evening',
    'travel', 'street', 'home', 'beach',
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AspectRatio(
            aspectRatio: 1,
            child: OutfitCollage(imageUrls: imageUrls, size: 200),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 10, 4, 10),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        outfit.name,
                        style: const TextStyle(
                            fontSize: 14, fontWeight: FontWeight.w600),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: Theme.of(context)
                              .colorScheme
                              .onSurface
                              .withValues(alpha: 0.08),
                          borderRadius: BorderRadius.circular(100),
                        ),
                        child: Text(outfit.tag,
                            style: TextStyle(
                                fontSize: 11,
                                color: Theme.of(context)
                                    .colorScheme
                                    .onSurface
                                    .withValues(alpha: 0.6))),
                      ),
                    ],
                  ),
                ),
                _ContextMenu(
                  outfit: outfit,
                  onEdit: onEdit,
                  tags: _tags,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ContextMenu extends ConsumerWidget {
  final OutfitModel outfit;
  final VoidCallback onEdit;
  final List<String> tags;

  const _ContextMenu({
    required this.outfit,
    required this.onEdit,
    required this.tags,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return PopupMenuButton<String>(
      icon: const Icon(Icons.more_vert, size: 20),
      onSelected: (value) async {
        if (value == 'edit') {
          onEdit();
        } else if (value == 'rename') {
          _showRenameSheet(context, ref);
        } else if (value == 'delete') {
          await ref.read(outfitsProvider.notifier).delete(outfit.id);
        }
      },
      itemBuilder: (_) => const [
        PopupMenuItem(value: 'edit', child: Text('Изменить образ')),
        PopupMenuItem(value: 'rename', child: Text('Переименовать')),
        PopupMenuItem(value: 'delete', child: Text('Удалить')),
      ],
    );
  }

  void _showRenameSheet(BuildContext context, WidgetRef ref) {
    final nameCtrl = TextEditingController(text: outfit.name);
    String selectedTag = outfit.tag;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setState) => Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 24,
            left: 24,
            right: 24,
            top: 24,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 36,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Theme.of(ctx)
                        .colorScheme
                        .onSurface
                        .withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Text('Редактировать',
                  style: Theme.of(ctx).textTheme.titleLarge),
              const SizedBox(height: 20),
              TextField(
                controller: nameCtrl,
                autofocus: true,
                decoration:
                    const InputDecoration(hintText: 'Название образа'),
              ),
              const SizedBox(height: 20),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: tags.map((tag) {
                  final selected = selectedTag == tag;
                  return GestureDetector(
                    onTap: () => setState(() => selectedTag = tag),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 180),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        color: selected
                            ? Theme.of(ctx).colorScheme.onSurface
                            : Theme.of(ctx).colorScheme.surface,
                        borderRadius: BorderRadius.circular(100),
                        border: Border.all(
                          color: Theme.of(ctx)
                              .colorScheme
                              .onSurface
                              .withValues(
                                  alpha: selected ? 0 : 0.15),
                        ),
                      ),
                      child: Text(
                        tag,
                        style: TextStyle(
                          fontSize: 14,
                          color: selected
                              ? Theme.of(ctx).colorScheme.surface
                              : Theme.of(ctx).colorScheme.onSurface,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: () async {
                  await ref.read(outfitsProvider.notifier).updateOutfit(
                        outfit.copyWith(
                          name: nameCtrl.text.trim(),
                          tag: selectedTag,
                        ),
                      );
                  if (ctx.mounted) Navigator.pop(ctx);
                },
                child: const Text('Сохранить'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
