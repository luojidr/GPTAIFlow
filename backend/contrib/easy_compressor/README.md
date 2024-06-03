### 需求：长文本(长字符串)压缩
###### * 要求：  
1) 压缩后的解压，文本必须之前一致，决不能允许压缩了，还原后的字符串变少(多)了或不一致  
2) 压缩与解压的性能尽可能适中
3) 多种压缩方案对比

###### 主要有以下方案对比：
1) 哈夫曼压缩(Huffman): 无损压缩算法  
2) LZW(Lempel-Ziv-Welch): 无损压缩算法  
3) Python 标准库的压缩模块: zlib, gzip, bz2, lzma ; zlib和gzip通常在速度上更快，但bz2和lzma在压缩率上可能更高
4) 其他压缩模块:  
    python-lz4: 非常快的压缩和解压缩库。它的压缩率可能不如zlib或bz2，但它的速度通常更快。  
	brotli: Google开发的一个用于压缩数据的新算法。它旨在为网络应用提供更好的压缩率。brotli 是一种无损压缩算法，特别适用于文本和HTML内容的压缩  
    python-snappy: Google开发的，旨在提供高速压缩和解压缩的库。它的压缩率不如其他一些算法，但是它的速度通常更快。  
    pylzma: Deprecated, 一个Python接口，用于访问LZMA SDK的功能。LZMA是一种非常高效的压缩算法，通常可以提供比bzip2更好的压缩率和更快的解压速度。Python 支持不是很好。 
    zstandard: Facebook开发的一种实时压缩算法，旨在提供最佳的压缩和解压缩速度。它提供了很高的压缩比和非常快的解压缩速度。(https://github.com/facebook/zstd) https://facebook.github.io/zstd/  
5) 可能有用的库: msgpack (序列化，但是比json更省空间), 但是肯定比压缩还是要大。
6) zstd 算法: python 可能支持不是很好，未考究
7) brotli 算法: python 可能支持不是很好，未考究
  

###### 参考链接:
   https://github.com/llgithubll/compress  
   https://github.com/lz4/lz4#readme  



