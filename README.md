# 2024-7-29 V1.3更新日志
1. 新增加了更新器，用户可以直接在软件里更新版本
2. 新增加了发行版功能，用户可以导出现成的游戏剧本，导出后无法再有后续新剧情。
3. 内置rembg安装包，用户部署更方便！
4. 新增ai音乐功能
5. 复了一些已知bug

# 2024-7-18 V1.2更新日志
1. 新增配置文件的可视化界面GUI,填写配置文件更方便
2. 新增分支选择模式，玩家可以选择ai提供的分支，或者自己填写，同时后续内容的生成速度可能会比先前的版本慢一点。
3. 修复了一些已知bug

# 2024-6-26 V1.1更新日志
1. 新增配置文件，一般设置用户可以直接在config.ini里进行配置，无需打开py文件
2. 新增ai绘画和ai语音的云端模式，再也不吃显卡啦
3. 新增了主题设置，剧本生成前用户可以自己设置剧情的主题
4. 修复了一些已知bug
5. 新增了一张壁纸


# 在开始使用之前
- ~~首先确保您有一台4GB显存以上，10系以上的显卡。用于运行ai绘画与ai语音~~ 1.1可以自己选择本地还是云端模式
- chatgpt的密钥（或者本地部署LLM）
- 安装好以下程序（云端模式无需理会1和2）：
1. stable diffusion
2. gpt-sovits(可以用其他替代，但是要自己改代码)
3. rembg（在整合包里有）


## 正式开始
### 在第一次打开游戏时，你首先要：
- 安装rembg
- 把onnx模型放到C:\Users\username/.u2net目录下
- 填写config.ini配置文件
- 如果使用gpt-sovits，请把参考音频放到gpt-sovits的go-weiui.bat的同一级目录下。
### 在运行程序之前，你首先要（云端模式忽略1和2）：
1. 运行stable diffusion的api
2. 运行gpt-sovits的api
3. 运行rembg的api
## 重启剧情
运行 重新开始新的游戏.bat

### 请从GUI.EXE中进入游戏，资源加载速度取决于您的电脑配置，请耐心等待

## 遇到报错
把log.txt的报错信息复制下来，私信我
## 许可证

本项目基于 [Ren'Py](https://www.renpy.org/) 项目进行二次开发，并遵循以下许可证条款：

- 本项目的主要部分遵循 [MIT 许可证](LICENSE)。
- 本项目中包含的某些组件和库遵循其他许可证，包括但不限于：
  - [GNU 宽通用公共许可证 (LGPL)](https://www.gnu.org/licenses/lgpl-3.0.html)
  - [Zlib 许可证](https://opensource.org/licenses/Zlib)
  - 其他相关许可证请参见各自的许可证文件。

请确保在分发本项目时，包含所有相关的许可证文件。



