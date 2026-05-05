class ProfileModel {
  final String id;
  final String name;
  final String gender; // 'male' | 'female' | 'nonbinary'
  final int? age;
  final int? heightCm;
  final int? weightKg;
  final String? clothingSize; // XS/S/M/L/XL/XXL
  final String? shoeSize;
  final String? bodyType;
  final String? photoFullUrl;
  final String? photoSideUrl;
  final String? photoFaceUrl;
  final StyleProfile? styleProfile;
  final DateTime createdAt;
  final DateTime updatedAt;

  const ProfileModel({
    required this.id,
    required this.name,
    required this.gender,
    this.age,
    this.heightCm,
    this.weightKg,
    this.clothingSize,
    this.shoeSize,
    this.bodyType,
    this.photoFullUrl,
    this.photoSideUrl,
    this.photoFaceUrl,
    this.styleProfile,
    required this.createdAt,
    required this.updatedAt,
  });

  bool get hasPhotos => photoFullUrl != null;
  bool get hasStyleProfile => styleProfile != null;

  ProfileModel copyWith({
    String? name,
    String? gender,
    int? age,
    int? heightCm,
    int? weightKg,
    String? clothingSize,
    String? shoeSize,
    String? bodyType,
    String? photoFullUrl,
    String? photoSideUrl,
    String? photoFaceUrl,
    StyleProfile? styleProfile,
  }) {
    return ProfileModel(
      id: id,
      name: name ?? this.name,
      gender: gender ?? this.gender,
      age: age ?? this.age,
      heightCm: heightCm ?? this.heightCm,
      weightKg: weightKg ?? this.weightKg,
      clothingSize: clothingSize ?? this.clothingSize,
      shoeSize: shoeSize ?? this.shoeSize,
      bodyType: bodyType ?? this.bodyType,
      photoFullUrl: photoFullUrl ?? this.photoFullUrl,
      photoSideUrl: photoSideUrl ?? this.photoSideUrl,
      photoFaceUrl: photoFaceUrl ?? this.photoFaceUrl,
      styleProfile: styleProfile ?? this.styleProfile,
      createdAt: createdAt,
      updatedAt: DateTime.now(),
    );
  }

  Map<String, dynamic> toFirestore() => {
        'name': name,
        'gender': gender,
        'age': age,
        'heightCm': heightCm,
        'weightKg': weightKg,
        'clothingSize': clothingSize,
        'shoeSize': shoeSize,
        'bodyType': bodyType,
        'photoFullUrl': photoFullUrl,
        'photoSideUrl': photoSideUrl,
        'photoFaceUrl': photoFaceUrl,
        'styleProfile': styleProfile?.toMap(),
        'createdAt': createdAt.toIso8601String(),
        'updatedAt': updatedAt.toIso8601String(),
      };

  factory ProfileModel.fromFirestore(String id, Map<String, dynamic> data) =>
      ProfileModel(
        id: id,
        name: data['name'] ?? '',
        gender: data['gender'] ?? 'nonbinary',
        age: data['age'],
        heightCm: data['heightCm'],
        weightKg: data['weightKg'],
        clothingSize: data['clothingSize'],
        shoeSize: data['shoeSize'],
        bodyType: data['bodyType'],
        photoFullUrl: data['photoFullUrl'],
        photoSideUrl: data['photoSideUrl'],
        photoFaceUrl: data['photoFaceUrl'],
        styleProfile: data['styleProfile'] != null
            ? StyleProfile.fromMap(data['styleProfile'])
            : null,
        createdAt: data['createdAt'] != null
            ? DateTime.parse(data['createdAt'] as String)
            : DateTime.now(),
        updatedAt: data['updatedAt'] != null
            ? DateTime.parse(data['updatedAt'] as String)
            : DateTime.now(),
      );
}

class StyleProfile {
  final String? colorType;
  final String? colorTypeDescription;
  final String? kibbeType;
  final String? kibbeDescription;
  final String? bodyShape;
  final String? bodyShapeDescription;
  final List<String> recommendedColors;
  final List<String> avoidColors;
  final List<String> recommendedCuts;
  final List<String> avoidCuts;
  final List<String> recommendedFabrics;
  final List<String> recommendedPatterns;
  final List<String> recommendedSilhouettes;
  final String? accessoryRecommendations;
  final String? hairstyleNotes;
  final String? proportionNotes;
  final String? generalAdvice;

  const StyleProfile({
    this.colorType,
    this.colorTypeDescription,
    this.kibbeType,
    this.kibbeDescription,
    this.bodyShape,
    this.bodyShapeDescription,
    this.recommendedColors = const [],
    this.avoidColors = const [],
    this.recommendedCuts = const [],
    this.avoidCuts = const [],
    this.recommendedFabrics = const [],
    this.recommendedPatterns = const [],
    this.recommendedSilhouettes = const [],
    this.accessoryRecommendations,
    this.hairstyleNotes,
    this.proportionNotes,
    this.generalAdvice,
  });

  Map<String, dynamic> toMap() => {
        'colorType': colorType,
        'colorTypeDescription': colorTypeDescription,
        'kibbeType': kibbeType,
        'kibbeDescription': kibbeDescription,
        'bodyShape': bodyShape,
        'bodyShapeDescription': bodyShapeDescription,
        'recommendedColors': recommendedColors,
        'avoidColors': avoidColors,
        'recommendedCuts': recommendedCuts,
        'avoidCuts': avoidCuts,
        'recommendedFabrics': recommendedFabrics,
        'recommendedPatterns': recommendedPatterns,
        'recommendedSilhouettes': recommendedSilhouettes,
        'accessoryRecommendations': accessoryRecommendations,
        'hairstyleNotes': hairstyleNotes,
        'proportionNotes': proportionNotes,
        'generalAdvice': generalAdvice,
      };

  factory StyleProfile.fromMap(Map<String, dynamic> m) => StyleProfile(
        colorType: m['colorType'],
        colorTypeDescription: m['colorTypeDescription'],
        kibbeType: m['kibbeType'],
        kibbeDescription: m['kibbeDescription'],
        bodyShape: m['bodyShape'],
        bodyShapeDescription: m['bodyShapeDescription'],
        recommendedColors: List<String>.from(m['recommendedColors'] ?? []),
        avoidColors: List<String>.from(m['avoidColors'] ?? []),
        recommendedCuts: List<String>.from(m['recommendedCuts'] ?? []),
        avoidCuts: List<String>.from(m['avoidCuts'] ?? []),
        recommendedFabrics: List<String>.from(m['recommendedFabrics'] ?? []),
        recommendedPatterns: List<String>.from(m['recommendedPatterns'] ?? []),
        recommendedSilhouettes:
            List<String>.from(m['recommendedSilhouettes'] ?? []),
        accessoryRecommendations: m['accessoryRecommendations'],
        hairstyleNotes: m['hairstyleNotes'],
        proportionNotes: m['proportionNotes'],
        generalAdvice: m['generalAdvice'],
      );
}
