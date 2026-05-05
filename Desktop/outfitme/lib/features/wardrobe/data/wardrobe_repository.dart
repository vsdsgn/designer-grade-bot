import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../services/storage/device_id_service.dart';
import '../domain/clothing_item_model.dart';

class WardrobeRepository {
  final _db = FirebaseFirestore.instance;
  String get _userId => DeviceIdService.instance.deviceId;

  CollectionReference get _col =>
      _db.collection('wardrobe').doc(_userId).collection('items');

  Stream<List<ClothingItemModel>> watchItems() {
    return _col
        .orderBy('addedAt', descending: true)
        .snapshots()
        .handleError((e) => throw Exception('Wardrobe stream error: $e'))
        .map((snap) => snap.docs
            .map((d) => ClothingItemModel.fromFirestore(
                d.id, d.data() as Map<String, dynamic>))
            .toList());
  }

  Future<List<ClothingItemModel>> getItems() async {
    try {
      final snap = await _col.orderBy('addedAt', descending: true).get();
      return snap.docs
          .map((d) => ClothingItemModel.fromFirestore(
              d.id, d.data() as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw Exception('Failed to load wardrobe: $e');
    }
  }

  Future<ClothingItemModel> addItem(ClothingItemModel item) async {
    try {
      await _col.doc(item.id).set(item.toFirestore());
      return item;
    } catch (e) {
      throw Exception('Failed to add item: $e');
    }
  }

  Future<void> updateItem(ClothingItemModel item) async {
    try {
      await _col.doc(item.id).update(item.toFirestore());
    } catch (e) {
      throw Exception('Failed to update item: $e');
    }
  }

  Future<void> deleteItem(String id) async {
    try {
      await _col.doc(id).delete();
    } catch (e) {
      throw Exception('Failed to delete item: $e');
    }
  }
}
