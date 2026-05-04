class OutfitModel {
  final String id;
  final String name;
  final String tag;
  final List<String> itemIds;
  final DateTime createdAt;

  const OutfitModel({
    required this.id,
    required this.name,
    required this.tag,
    required this.itemIds,
    required this.createdAt,
  });

  OutfitModel copyWith({String? name, String? tag}) {
    return OutfitModel(
      id: id,
      name: name ?? this.name,
      tag: tag ?? this.tag,
      itemIds: itemIds,
      createdAt: createdAt,
    );
  }

  Map<String, dynamic> toFirestore() => {
        'name': name,
        'tag': tag,
        'itemIds': itemIds,
        'createdAt': createdAt.toIso8601String(),
      };

  factory OutfitModel.fromFirestore(String id, Map<String, dynamic> data) {
    return OutfitModel(
      id: id,
      name: data['name'] ?? '',
      tag: data['tag'] ?? 'casual',
      itemIds: List<String>.from(data['itemIds'] ?? []),
      createdAt: data['createdAt'] != null
          ? DateTime.parse(data['createdAt'])
          : DateTime.now(),
    );
  }
}
