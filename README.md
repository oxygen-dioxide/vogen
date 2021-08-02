# PyVogen
[Github](https://github.com/oxygen-dioxide/vogen) | 
[Gitee](https://gitee.com/oxygendioxide/vogen) | 
[Gitlab](https://gitlab.com/oxygen-dioxide/vogen) | 
[Bitbucket](https://bitbucket.org/oxygendioxide/vogen) 

PyVogen是开源歌声合成引擎[Vogen](https://github.com/aqtq314/Vogen.Client)的python实现

本python库依赖以下库：

[numpy](https://numpy.org/) 
[jyutping](https://github.com/imdreamrunner/python-jyutping)
[pypinyin](https://pypinyin.readthedocs.io/zh_CN/master/)
[onnxruntime](https://www.onnxruntime.ai/)
[pyworld](https://github.com/JeremyCCHsu/Python-Wrapper-for-World-Vocoder)

## 安装
暂未上架pypi，请自行下载，将vogen文件夹复制到python安装目录下的Lib文件夹下

## 示例

以下是文件读写示例，音频合成等更多示例参见[示例列表](.\examples)

```py
import vogen as vg

#打开文件
vf=vg.openvog("myproject.vog")

# 获取第0乐句的歌词与拼音列表
u=vf.utts[0]
lyrics=[i.lyric for i in u.notes]
roms=[i.rom for i in u.notes]
print(lyrics)
print(roms)

#保存文件
vf.save("myproject2.vog")
```

# 相关链接
[vogen仓库](https://github.com/aqtq314/Vogen.Client)

[vogen作者的b站空间（vogen试听页面）](https://space.bilibili.com/169955)