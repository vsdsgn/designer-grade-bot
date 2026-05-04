import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import '../../data/outfits_repository.dart';
import '../../domain/outfit_model.dart';
import '../../../../features/tryon/domain/outfit_session.dart';

final _repo = OutfitsRepository();

final outfitsProvider =
    AsyncNotifierProvider<OutfitsNotifier, List<OutfitModel>>(
  OutfitsNotifier.new,
);

class OutfitsNotifier extends AsyncNotifier<List<OutfitModel>> {
  @override
  Future<List<OutfitModel>> build() async {
    final sub = _repo.watchOutfits().listen((outfits) {
      state = AsyncData(outfits);
    });
    ref.onDispose(sub.cancel);
    return _repo.watchOutfits().first;
  }

  Future<void> save(String name, String tag, OutfitSession session) async {
    final outfit = OutfitModel(
      id: const Uuid().v4(),
      name: name,
      tag: tag,
      itemIds: session.allItemIds,
      createdAt: DateTime.now(),
    );
    await _repo.saveOutfit(outfit);
  }

  Future<void> updateOutfit(OutfitModel outfit) async {
    await _repo.updateOutfit(outfit);
  }

  Future<void> delete(String id) async {
    await _repo.deleteOutfit(id);
  }
}
