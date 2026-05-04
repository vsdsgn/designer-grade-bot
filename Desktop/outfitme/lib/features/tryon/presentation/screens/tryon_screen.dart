import 'dart:io';
import 'dart:ui' as ui;
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:share_plus/share_plus.dart';
import 'package:path_provider/path_provider.dart';
import '../../../outfits/presentation/providers/outfits_provider.dart';
import '../../../profile/presentation/providers/profile_provider.dart';
import '../../../wardrobe/presentation/providers/wardrobe_provider.dart';
import '../providers/tryon_provider.dart';
import '../widgets/item_picker_panel.dart';
import '../widgets/active_items_strip.dart';
import '../../domain/outfit_session.dart';

class TryOnScreen extends ConsumerStatefulWidget {
  const TryOnScreen({super.key});

  @override
  ConsumerState<TryOnScreen> createState() => _TryOnScreenState();
}

class _TryOnScreenState extends ConsumerState<TryOnScreen> {
  final _canvasKey = GlobalKey();

  @override
  Widget build(BuildContext context) {
    final session = ref.watch(tryOnSessionProvider);
    final profileAsync = ref.watch(profileProvider);
    final wardrobeAsync = ref.watch(wardrobeStreamProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // ── Canvas: model photo ─────────────────────────
          RepaintBoundary(
            key: _canvasKey,
            child: _ModelCanvas(profileAsync: profileAsync),
          ),

          // ── Top bar ────────────────────────────────────
          _TopBar(
            session: session,
            onShare: () => _shareOutfit(session),
            onClear: () => ref.read(tryOnSessionProvider.notifier).clear(),
          ),

          // ── Active items strip (selected items row) ─────
          if (!session.isEmpty)
            Positioned(
              left: 0,
              right: 0,
              bottom: 280,
              child: ActiveItemsStrip(
                session: session,
                onRemove: (item) =>
                    ref.read(tryOnSessionProvider.notifier).remove(item),
              ),
            ),

          // ── Bottom item picker panel ────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: wardrobeAsync.when(
              data: (items) => ItemPickerPanel(
                items: items,
                session: session,
                onToggle: (item) =>
                    ref.read(tryOnSessionProvider.notifier).toggle(item),
                onSave: session.meetsMinimum
                    ? () => _showSaveModal(context, session)
                    : null,
                onRate: session.meetsMinimum
                    ? () => _showRatingModal(context, session)
                    : null,
                onShare: () => _shareOutfit(session),
              ),
              loading: () => const SizedBox(height: 220),
              error: (e, _) => const SizedBox(height: 220),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _shareOutfit(OutfitSession session) async {
    try {
      final boundary = _canvasKey.currentContext?.findRenderObject()
          as RenderRepaintBoundary?;
      if (boundary == null) return;

      final image = await boundary.toImage(pixelRatio: 2.0);
      final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
      if (bytes == null) return;

      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/outfit_share.png');
      await file.writeAsBytes(bytes.buffer.asUint8List());

      await Share.shareXFiles(
        [XFile(file.path)],
        text: 'Мой образ в OutfitMe 👗',
      );
    } catch (_) {}
  }

  void _showSaveModal(BuildContext context, OutfitSession session) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _SaveOutfitSheet(session: session),
    );
  }

  void _showRatingModal(BuildContext context, OutfitSession session) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _RatingSheet(session: session),
    );
  }
}

// ── Model canvas ──────────────────────────────────────────────────────────────

class _ModelCanvas extends ConsumerWidget {
  final AsyncValue profileAsync;
  const _ModelCanvas({required this.profileAsync});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return profileAsync.when(
      loading: () => const SizedBox.expand(),
      error: (e, stack) => _silhouette(context, 'nonbinary'),
      data: (profile) {
        if (profile == null || profile.photoFullUrl == null) {
          return _silhouette(context, profile?.gender ?? 'nonbinary');
        }
        return InteractiveViewer(
          minScale: 0.8,
          maxScale: 4.0,
          child: SizedBox.expand(
            child: CachedNetworkImage(
              imageUrl: profile.photoFullUrl!,
              fit: BoxFit.contain,
              alignment: Alignment.topCenter,
            ),
          ),
        );
      },
    );
  }

  Widget _silhouette(BuildContext context, String gender) {
    final icon = gender == 'female'
        ? Icons.person_outline
        : Icons.person_outline;
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, size: 120, color: Colors.white.withValues(alpha: 0.15)),
        const SizedBox(height: 16),
        Text(
          'Загрузи фото в профиле\nдля точной примерки',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Colors.white.withValues(alpha: 0.4),
            fontSize: 14,
          ),
        ),
      ],
    );
  }
}

// ── Top bar ───────────────────────────────────────────────────────────────────

class _TopBar extends StatelessWidget {
  final OutfitSession session;
  final VoidCallback onShare;
  final VoidCallback onClear;

  const _TopBar({
    required this.session,
    required this.onShare,
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: 0,
      left: 0,
      right: 0,
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'OutfitMe',
                style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.9),
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.3,
                ),
              ),
              Row(
                children: [
                  if (!session.isEmpty) ...[
                    _IconBtn(
                      icon: Icons.share_outlined,
                      onTap: onShare,
                    ),
                    const SizedBox(width: 8),
                    _IconBtn(
                      icon: Icons.clear,
                      onTap: onClear,
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _IconBtn extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;

  const _IconBtn({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.15),
          shape: BoxShape.circle,
        ),
        child: Icon(icon, color: Colors.white, size: 18),
      ),
    );
  }
}

// ── Save outfit sheet ─────────────────────────────────────────────────────────

class _SaveOutfitSheet extends ConsumerStatefulWidget {
  final OutfitSession session;
  const _SaveOutfitSheet({required this.session});

  @override
  ConsumerState<_SaveOutfitSheet> createState() => _SaveOutfitSheetState();
}

class _SaveOutfitSheetState extends ConsumerState<_SaveOutfitSheet> {
  final _nameCtrl = TextEditingController();
  String? _selectedTag;
  bool _saving = false;

  static const _tags = [
    'casual', 'formal', 'sport', 'evening',
    'travel', 'street', 'home', 'beach',
  ];

  @override
  void dispose() {
    _nameCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
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
                color: Theme.of(context)
                    .colorScheme
                    .onSurface
                    .withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 20),
          Text('Сохранить образ',
              style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 20),
          TextField(
            controller: _nameCtrl,
            autofocus: true,
            decoration: const InputDecoration(hintText: 'Название образа'),
          ),
          const SizedBox(height: 20),
          Text('Стиль', style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _tags.map((tag) {
              final selected = _selectedTag == tag;
              return GestureDetector(
                onTap: () => setState(() => _selectedTag = tag),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 180),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: selected
                        ? Theme.of(context).colorScheme.onSurface
                        : Theme.of(context).colorScheme.surface,
                    borderRadius: BorderRadius.circular(100),
                    border: Border.all(
                      color: Theme.of(context)
                          .colorScheme
                          .onSurface
                          .withValues(alpha: selected ? 0 : 0.15),
                    ),
                  ),
                  child: Text(
                    tag,
                    style: TextStyle(
                      fontSize: 14,
                      color: selected
                          ? Theme.of(context).colorScheme.surface
                          : Theme.of(context).colorScheme.onSurface,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: _saving || _nameCtrl.text.trim().isEmpty
                ? null
                : _save,
            child: _saving
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Сохранить'),
          ),
        ],
      ),
    );
  }

  Future<void> _save() async {
    if (_nameCtrl.text.trim().isEmpty) return;
    setState(() => _saving = true);
    await ref.read(outfitsProvider.notifier).save(
          _nameCtrl.text.trim(),
          _selectedTag ?? 'casual',
          widget.session,
        );
    if (mounted) Navigator.pop(context);
  }
}

// ── Rating sheet (placeholder, full impl in Этап 4) ──────────────────────────

class _RatingSheet extends StatelessWidget {
  final OutfitSession session;
  const _RatingSheet({required this.session});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 36,
            height: 4,
            decoration: BoxDecoration(
              color: Theme.of(context)
                  .colorScheme
                  .onSurface
                  .withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 24),
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text('Оцениваем образ...',
              style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}
