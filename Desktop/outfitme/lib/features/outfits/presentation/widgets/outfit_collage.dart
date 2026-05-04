import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

class OutfitCollage extends StatelessWidget {
  final List<String> imageUrls;
  final double size;

  const OutfitCollage({
    super.key,
    required this.imageUrls,
    this.size = 160,
  });

  @override
  Widget build(BuildContext context) {
    final urls = imageUrls.take(4).toList();

    if (urls.isEmpty) {
      return _placeholder(size);
    }

    if (urls.length == 1) {
      return _image(urls[0], size, size);
    }

    if (urls.length == 2) {
      return SizedBox(
        width: size,
        height: size,
        child: Row(
          children: [
            _image(urls[0], size / 2 - 1, size),
            const SizedBox(width: 2),
            _image(urls[1], size / 2 - 1, size),
          ],
        ),
      );
    }

    // 3 or 4 items: 2x2 grid
    return SizedBox(
      width: size,
      height: size,
      child: Column(
        children: [
          Row(
            children: [
              _image(urls[0], size / 2 - 1, size / 2 - 1),
              const SizedBox(width: 2),
              _image(urls[1], size / 2 - 1, size / 2 - 1),
            ],
          ),
          const SizedBox(height: 2),
          Row(
            children: [
              _image(urls[2], size / 2 - 1, size / 2 - 1),
              const SizedBox(width: 2),
              if (urls.length >= 4)
                _image(urls[3], size / 2 - 1, size / 2 - 1)
              else
                SizedBox(width: size / 2 - 1, height: size / 2 - 1),
            ],
          ),
        ],
      ),
    );
  }

  Widget _image(String url, double w, double h) {
    return CachedNetworkImage(
      imageUrl: url,
      width: w,
      height: h,
      fit: BoxFit.cover,
      errorWidget: (_, _, _) => _placeholder(w),
    );
  }

  Widget _placeholder(double w) {
    return Container(
      width: w,
      height: w,
      color: Colors.grey.shade200,
      child: Icon(Icons.checkroom_outlined,
          size: w * 0.4, color: Colors.grey.shade400),
    );
  }
}
