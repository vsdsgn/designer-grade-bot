import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_constants.dart';
import '../../domain/profile_model.dart';
import '../providers/profile_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(profileProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Профиль'),
        centerTitle: true,
        actions: [
          profileAsync.valueOrNull != null
              ? IconButton(
                  icon: const Icon(Icons.edit_outlined),
                  onPressed: () =>
                      _showEditSheet(context, ref, profileAsync.value!),
                )
              : const SizedBox.shrink(),
        ],
      ),
      body: profileAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Ошибка: $e')),
        data: (profile) {
          if (profile == null) {
            return const Center(child: Text('Профиль не найден'));
          }
          return _ProfileBody(profile: profile);
        },
      ),
    );
  }

  void _showEditSheet(BuildContext context, WidgetRef ref, ProfileModel profile) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _EditSheet(profile: profile),
    );
  }
}

// ── Profile body ──────────────────────────────────────────────────────────────

class _ProfileBody extends StatelessWidget {
  final ProfileModel profile;
  const _ProfileBody({required this.profile});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        _AvatarSection(profile: profile),
        const SizedBox(height: 32),
        _ParamsSection(profile: profile),
        if (profile.hasStyleProfile) ...[
          const SizedBox(height: 24),
          _StyleSection(style: profile.styleProfile!),
        ],
        const SizedBox(height: 32),
        _ResetButton(),
      ],
    );
  }
}

// ── Avatar ────────────────────────────────────────────────────────────────────

class _AvatarSection extends StatelessWidget {
  final ProfileModel profile;
  const _AvatarSection({required this.profile});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        CircleAvatar(
          radius: 52,
          backgroundColor:
              Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.08),
          foregroundImage: profile.photoFaceUrl != null
              ? CachedNetworkImageProvider(profile.photoFaceUrl!)
              : profile.photoFullUrl != null
                  ? CachedNetworkImageProvider(profile.photoFullUrl!)
                  : null,
          child: profile.photoFaceUrl == null && profile.photoFullUrl == null
              ? Text(
                  profile.name.isNotEmpty
                      ? profile.name[0].toUpperCase()
                      : '?',
                  style: const TextStyle(
                      fontSize: 36, fontWeight: FontWeight.w600),
                )
              : null,
        ),
        const SizedBox(height: 16),
        Text(
          profile.name,
          style: Theme.of(context)
              .textTheme
              .headlineSmall
              ?.copyWith(fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 4),
        Text(
          _genderLabel(profile.gender),
          style: TextStyle(
              color: Theme.of(context)
                  .colorScheme
                  .onSurface
                  .withValues(alpha: 0.5)),
        ),
      ],
    );
  }

  String _genderLabel(String g) => switch (g) {
        'male' => 'Мужской',
        'female' => 'Женский',
        _ => 'Небинарный',
      };
}

// ── Params ────────────────────────────────────────────────────────────────────

class _ParamsSection extends StatelessWidget {
  final ProfileModel profile;
  const _ParamsSection({required this.profile});

  @override
  Widget build(BuildContext context) {
    final items = <(String, String?)>[
      ('Возраст', profile.age != null ? '${profile.age} лет' : null),
      ('Рост', profile.heightCm != null ? '${profile.heightCm} см' : null),
      ('Вес', profile.weightKg != null ? '${profile.weightKg} кг' : null),
      ('Размер одежды', profile.clothingSize),
      ('Размер обуви', profile.shoeSize),
      ('Тип фигуры', profile.bodyType),
    ].where((e) => e.$2 != null).toList();

    if (items.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Параметры',
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.w700)),
        const SizedBox(height: 12),
        Container(
          decoration: BoxDecoration(
            color: Theme.of(context)
                .colorScheme
                .onSurface
                .withValues(alpha: 0.04),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            children: items.asMap().entries.map((e) {
              final isLast = e.key == items.length - 1;
              return Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 14),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(e.value.$1,
                            style: TextStyle(
                                color: Theme.of(context)
                                    .colorScheme
                                    .onSurface
                                    .withValues(alpha: 0.6))),
                        Text(e.value.$2!,
                            style: const TextStyle(
                                fontWeight: FontWeight.w500)),
                      ],
                    ),
                  ),
                  if (!isLast)
                    Divider(
                      height: 1,
                      indent: 16,
                      endIndent: 16,
                      color: Theme.of(context)
                          .colorScheme
                          .onSurface
                          .withValues(alpha: 0.08),
                    ),
                ],
              );
            }).toList(),
          ),
        ),
      ],
    );
  }
}

// ── Style profile ─────────────────────────────────────────────────────────────

class _StyleSection extends StatelessWidget {
  final StyleProfile style;
  const _StyleSection({required this.style});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Стиль-профиль',
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.w700)),
        const SizedBox(height: 12),
        if (style.colorType != null)
          _InfoCard(
            icon: Icons.palette_outlined,
            title: 'Цветотип',
            value: style.colorType!,
            subtitle: style.colorTypeDescription,
          ),
        if (style.kibbeType != null) ...[
          const SizedBox(height: 8),
          _InfoCard(
            icon: Icons.accessibility_new_outlined,
            title: 'Тип по Кибби',
            value: style.kibbeType!,
            subtitle: style.kibbeDescription,
          ),
        ],
        if (style.recommendedColors.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text('Рекомендуемые цвета',
              style: TextStyle(
                  fontSize: 13,
                  color: Theme.of(context)
                      .colorScheme
                      .onSurface
                      .withValues(alpha: 0.5))),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 6,
            children: style.recommendedColors
                .map((c) => _Chip(label: c, positive: true))
                .toList(),
          ),
        ],
        if (style.avoidColors.isNotEmpty) ...[
          const SizedBox(height: 12),
          Text('Избегать',
              style: TextStyle(
                  fontSize: 13,
                  color: Theme.of(context)
                      .colorScheme
                      .onSurface
                      .withValues(alpha: 0.5))),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 6,
            children: style.avoidColors
                .map((c) => _Chip(label: c, positive: false))
                .toList(),
          ),
        ],
        if (style.generalAdvice != null) ...[
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context)
                  .colorScheme
                  .onSurface
                  .withValues(alpha: 0.04),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Совет стилиста',
                    style: const TextStyle(
                        fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 8),
                Text(style.generalAdvice!,
                    style: TextStyle(
                        fontSize: 13,
                        height: 1.5,
                        color: Theme.of(context)
                            .colorScheme
                            .onSurface
                            .withValues(alpha: 0.7))),
              ],
            ),
          ),
        ],
      ],
    );
  }
}

class _InfoCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final String? subtitle;

  const _InfoCard({
    required this.icon,
    required this.title,
    required this.value,
    this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.04),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Icon(icon, size: 20,
              color: Theme.of(context)
                  .colorScheme
                  .onSurface
                  .withValues(alpha: 0.4)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: TextStyle(
                        fontSize: 12,
                        color: Theme.of(context)
                            .colorScheme
                            .onSurface
                            .withValues(alpha: 0.5))),
                const SizedBox(height: 2),
                Text(value,
                    style: const TextStyle(fontWeight: FontWeight.w600)),
                if (subtitle != null) ...[
                  const SizedBox(height: 2),
                  Text(subtitle!,
                      style: TextStyle(
                          fontSize: 12,
                          color: Theme.of(context)
                              .colorScheme
                              .onSurface
                              .withValues(alpha: 0.5))),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  final String label;
  final bool positive;
  const _Chip({required this.label, required this.positive});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: positive
            ? Colors.green.withValues(alpha: 0.1)
            : Colors.red.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(100),
        border: Border.all(
          color: positive
              ? Colors.green.withValues(alpha: 0.3)
              : Colors.red.withValues(alpha: 0.2),
        ),
      ),
      child: Text(label,
          style: TextStyle(
              fontSize: 12,
              color: positive ? Colors.green.shade700 : Colors.red.shade400)),
    );
  }
}

// ── Reset button ──────────────────────────────────────────────────────────────

class _ResetButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: () => _confirmReset(context),
      child: Text('Сбросить профиль',
          style: TextStyle(color: Colors.red.shade400)),
    );
  }

  void _confirmReset(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Сбросить профиль?'),
        content: const Text(
            'Онбординг запустится заново. Гардероб и образы сохранятся.'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Отмена')),
          TextButton(
            onPressed: () async {
              final prefs = await SharedPreferences.getInstance();
              await prefs.remove(AppConstants.onboardingCompleteKey);
              if (ctx.mounted) {
                Navigator.pop(ctx);
                context.go('/onboarding');
              }
            },
            child: Text('Сбросить',
                style: TextStyle(color: Colors.red.shade400)),
          ),
        ],
      ),
    );
  }
}

// ── Edit sheet ────────────────────────────────────────────────────────────────

class _EditSheet extends ConsumerStatefulWidget {
  final ProfileModel profile;
  const _EditSheet({required this.profile});

  @override
  ConsumerState<_EditSheet> createState() => _EditSheetState();
}

class _EditSheetState extends ConsumerState<_EditSheet> {
  late final TextEditingController _nameCtrl;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _nameCtrl = TextEditingController(text: widget.profile.name);
  }

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
          Text('Редактировать профиль',
              style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 20),
          TextField(
            controller: _nameCtrl,
            autofocus: true,
            decoration: const InputDecoration(labelText: 'Имя'),
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: _saving ? null : _save,
            child: _saving
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Сохранить'),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }

  Future<void> _save() async {
    if (_nameCtrl.text.trim().isEmpty) return;
    setState(() => _saving = true);
    await ref.read(profileNotifierProvider.notifier).save(
          widget.profile.copyWith(name: _nameCtrl.text.trim()),
        );
    if (mounted) Navigator.pop(context);
  }
}
