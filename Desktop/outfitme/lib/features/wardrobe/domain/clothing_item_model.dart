import '../../../../core/constants/slot_constants.dart';

class ClothingItemModel {
  final String id;
  final String name;
  final String category;
  final ClothingSlot slot;
  final ClothingSubType subType;
  final String originalUrl;
  final String? processedUrl; // remove.bg result
  final String? color;
  final String? secondaryColor;
  final String? season;
  final String? style;
  final String? pattern;
  final bool isProcessing;
  final DateTime addedAt;

  const ClothingItemModel({
    required this.id,
    required this.name,
    required this.category,
    required this.slot,
    required this.subType,
    required this.originalUrl,
    this.processedUrl,
    this.color,
    this.secondaryColor,
    this.season,
    this.style,
    this.pattern,
    this.isProcessing = false,
    required this.addedAt,
  });

  // The URL to show in UI — prefer processed if ready
  String get displayUrl => processedUrl ?? originalUrl;

  bool get hasProcessedPhoto => processedUrl != null;

  ClothingItemModel copyWith({
    String? name,
    String? category,
    ClothingSlot? slot,
    ClothingSubType? subType,
    String? originalUrl,
    String? processedUrl,
    String? color,
    String? secondaryColor,
    String? season,
    String? style,
    String? pattern,
    bool? isProcessing,
  }) {
    return ClothingItemModel(
      id: id,
      name: name ?? this.name,
      category: category ?? this.category,
      slot: slot ?? this.slot,
      subType: subType ?? this.subType,
      originalUrl: originalUrl ?? this.originalUrl,
      processedUrl: processedUrl ?? this.processedUrl,
      color: color ?? this.color,
      secondaryColor: secondaryColor ?? this.secondaryColor,
      season: season ?? this.season,
      style: style ?? this.style,
      pattern: pattern ?? this.pattern,
      isProcessing: isProcessing ?? this.isProcessing,
      addedAt: addedAt,
    );
  }

  Map<String, dynamic> toFirestore() => {
        'name': name,
        'category': category,
        'slot': slot.name,
        'subType': subType.name,
        'originalUrl': originalUrl,
        'processedUrl': processedUrl,
        'color': color,
        'secondaryColor': secondaryColor,
        'season': season,
        'style': style,
        'pattern': pattern,
        'isProcessing': isProcessing,
        'addedAt': addedAt.toIso8601String(),
      };

  factory ClothingItemModel.fromFirestore(
      String id, Map<String, dynamic> data) {
    return ClothingItemModel(
      id: id,
      name: data['name'] ?? '',
      category: data['category'] ?? '',
      slot: ClothingSlot.values.firstWhere(
        (s) => s.name == data['slot'],
        orElse: () => ClothingSlot.accessories,
      ),
      subType: ClothingSubType.values.firstWhere(
        (s) => s.name == data['subType'],
        orElse: () => ClothingSubType.jewelry,
      ),
      originalUrl: data['originalUrl'] ?? '',
      processedUrl: data['processedUrl'],
      color: data['color'],
      secondaryColor: data['secondaryColor'],
      season: data['season'],
      style: data['style'],
      pattern: data['pattern'],
      isProcessing: data['isProcessing'] ?? false,
      addedAt: data['addedAt'] != null
          ? DateTime.parse(data['addedAt'] as String)
          : DateTime.now(),
    );
  }
}
