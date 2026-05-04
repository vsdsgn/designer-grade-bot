import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../services/storage/device_id_service.dart';
import '../domain/outfit_model.dart';

class OutfitsRepository {
  final _db = FirebaseFirestore.instance;
  String get _userId => DeviceIdService.instance.deviceId;

  CollectionReference get _col =>
      _db.collection('outfits').doc(_userId).collection('items');

  Stream<List<OutfitModel>> watchOutfits() {
    return _col
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snap) => snap.docs
            .map((d) => OutfitModel.fromFirestore(
                d.id, d.data() as Map<String, dynamic>))
            .toList());
  }

  Future<void> saveOutfit(OutfitModel outfit) async {
    await _col.doc(outfit.id).set(outfit.toFirestore());
  }

  Future<void> updateOutfit(OutfitModel outfit) async {
    await _col.doc(outfit.id).update({
      'name': outfit.name,
      'tag': outfit.tag,
    });
  }

  Future<void> deleteOutfit(String id) async {
    await _col.doc(id).delete();
  }
}
