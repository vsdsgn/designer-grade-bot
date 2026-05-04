import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/outfit_session.dart';
import '../../../wardrobe/domain/clothing_item_model.dart';

final tryOnSessionProvider =
    NotifierProvider<TryOnNotifier, OutfitSession>(TryOnNotifier.new);

// Currently active slot filter for the item picker panel
final activePanelSlotProvider = StateProvider<int>((ref) => 0);

class TryOnNotifier extends Notifier<OutfitSession> {
  @override
  OutfitSession build() => const OutfitSession();

  void toggle(ClothingItemModel item) {
    state = state.toggleItem(item);
  }

  void remove(ClothingItemModel item) {
    state = state.removeItem(item);
  }

  void clear() {
    state = state.clear();
  }

  /// Load a saved outfit back into the session
  void loadItems(List<ClothingItemModel> items) {
    var session = const OutfitSession();
    for (final item in items) {
      session = session.addItem(item);
    }
    state = session;
  }

  void loadOutfit(List<ClothingItemModel> items) => loadItems(items);
}
