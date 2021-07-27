# vogen
[Github](https://github.com/oxygen-dioxide/vogen) | 
[Gitee](https://gitee.com/oxygendioxide/vogen)
[Gitlab](https://gitlab.com/oxygen-dioxide/vogen)
[Bitbucket](https://bitbucket.org/oxygendioxide/vogen)

读写[vogen](https://github.com/aqtq314/Vogen.Client) .vog文件的python库

## 安装
暂未上架pypi，请自行下载，将vogen文件夹复制到python安装目录下的Lib文件夹下

## 示例
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