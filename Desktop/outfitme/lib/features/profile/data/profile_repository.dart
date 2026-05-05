import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../services/storage/device_id_service.dart';
import '../domain/profile_model.dart';

class ProfileRepository {
  final _firestore = FirebaseFirestore.instance;

  String get _userId => DeviceIdService.instance.deviceId;
  DocumentReference get _doc =>
      _firestore.collection('users').doc(_userId).collection('data').doc('profile');

  Future<ProfileModel?> getProfile() async {
    try {
      final snap = await _doc.get();
      if (!snap.exists) return null;
      return ProfileModel.fromFirestore(_userId, snap.data() as Map<String, dynamic>);
    } catch (e) {
      throw Exception('Failed to load profile: $e');
    }
  }

  Future<void> saveProfile(ProfileModel profile) async {
    try {
      await _doc.set(profile.toFirestore(), SetOptions(merge: true));
    } catch (e) {
      throw Exception('Failed to save profile: $e');
    }
  }

  Stream<ProfileModel?> watchProfile() {
    return _doc
        .snapshots()
        .handleError((e) => throw Exception('Profile stream error: $e'))
        .map((snap) {
      if (!snap.exists) return null;
      return ProfileModel.fromFirestore(_userId, snap.data() as Map<String, dynamic>);
    });
  }
}
