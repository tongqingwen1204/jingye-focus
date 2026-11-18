# 静叶 · 专注入口

把系统自带的「专注模式」，做成桌面上的一块组件、控制中心里的一个磁贴、长按图标的一个快捷方式。

> **免责声明**：本项目为非官方工具，与小米公司无任何关联，未经小米授权或认可。
> 「小米」「红米」「澎湃 OS」「MIUI」为其权利人商标，此处仅用于说明适配环境。
> 本项目不绕过任何系统限制：专注模式该多久还是多久，无法中途退出，这是系统行为。
> 系统后续版本若修改内部 Activity 名，本工具会退化为「打开系统设置」，属预期内的失效方式，不承诺永久可用。

> 本应用不申请任何权限、不联网、不含第三方 SDK，只做一件事：拉起系统自带的专注模式页面。

- 安装包：见 [Releases](../../releases) 中的 `jingye-focus-1.0.apk`（192 KB，Android 10+，无需 root、不联网）
- 效果预览：`docs/preview.html`（按 DP 还原的视觉稿，非实机截图）
- 设计/规范说明：`docs/spec-compliance.md`

## 为什么需要它

澎湃 OS 的专注模式（开启后只能用相机和紧急呼叫，到点才退出）藏在
`设置 → 健康使用手机 → 今日屏幕使用时长 → 右上角树叶图标`，或者只能在设置里搜「专注模式」。
它没有桌面图标，也没有官方桌面组件——系统里连一个可以直接点的入口都没有。

但系统设置里其实存在一个**对外导出**的 Activity：

```
com.xiaomi.misettings/com.xiaomi.misettings.usagestats.FocusSettingsMainActivity
```

任何应用都可以直接拉起它（这也是「创建快捷方式」这类 App 能在桌面做出专注模式图标的原因）。
这个工程就是把这一行 Intent 包装成一个合规的桌面组件。

## 四种组件 + 两个系统入口

| 入口 | 名称 | 视觉 | 交互 |
| --- | --- | --- | --- |
| 桌面组件 1×1 | 专注小格 | 淡蓝底 + 人像，**不带文字** | 点整格 → 专注模式 |
| 桌面组件 1×1 | 屏幕用时 | 淡蓝底 + 时钟，**不带文字** | 点整格 → 屏幕使用时间 |
| 桌面组件 2×2 | 专注入口 | 淡蓝渐变卡 + 撑满的人像，**不带文字** | 点整块卡片 → 系统专注模式页面 |
| 桌面组件 4×2 | 专注与屏幕时间 | 左：人像横排文案；右：时钟 | 左热区 → 专注模式，右侧 → 屏幕时间 |
| 控制中心磁贴 | 专注模式 | 人像剪影 | 下拉控制中心点一下（锁屏时先解锁） |
| 长按桌面图标 | 进入专注 | — | 静态快捷方式，一步直达 |

两个 1×1 是同一套逻辑的两个实例（`CompactWidgetProvider` 抽象基类 + 两个子类），
差别只有布局和跳转目标，改一处不影响另一处。

组件本身不显示任何用户数据，不做网络请求，点击即跳转，属于「功能直达」型小部件。

### 那为什么不用「创建快捷方式」这类 App？

说得直接点：**功能上确实重叠**。市面上现成的快捷方式工具也能在桌面放一个专注模式图标，
如果你已经装了、并且够用，那这个项目对你没有价值。差别只有三点：

1. **组件是照小米小部件规范做的**：四种尺寸各自设计过，圆角 18dp（2K 下 21dp）、安全区 16dp、
   深浅两套预览图，不是把一个图标塞进默认模板；
2. **跳转链有 `exported` 校验 + 四级回退**，系统改类名也不会变成死键，会退到屏幕时间页或系统设置；
3. **零权限、不联网、无第三方库、无 AndroidX**，192 KB，全部源码 300 多行就在这个仓库里，可以自己读完。

就这些，没有更玄的东西。

## 安装

从 [Releases](../../releases) 下载 `jingye-focus-1.0.apk`，然后：

```bash
adb install -r jingye-focus-1.0.apk
```

或者把 APK 传到手机点开安装（首次需要在「安装未知应用」里允许文件管理器/浏览器）。
校验值（SHA-256）：`2708e82776d268192dab9ad01c9efd5bca56b6b46df30ee42e974bdca916889a`

> 仓库里不存放 APK（二进制不进版本库），只放在 Release 附件。
> 想自己出包见下文「重新构建」，产物落在 `dist/`。
> 自己构建出来的包**签名与本 Release 不同**，无法覆盖安装，需要先卸载旧版。

装完会看到一个叫「静叶」的应用，界面只有一颗「进入专注模式」按钮，点一下直达系统页面。
组件和磁贴按下一节的方式添加。

## 添加组件

正确路径（侧载应用的组件不在小米小部件中心的索引里，只能从「安卓小部件」列表里找）：

1. 长按桌面空白处 → 「添加小组件」
2. 选「全部应用」→ 切到「安卓小部件」
3. 拉到列表最下方，看到「静叶」的四个组件
4. 长按想要的拖到桌面：1×1 有「专注小格」「屏幕用时」，2×2 是「专注入口」，4×2 是「专注与屏幕时间」

控制中心磁贴：下拉控制中心 → 编辑按钮 → 找到「专注模式」拖到常用区域。

## 图标怎么来的

组件与图标里的人像来自一张自制抠图（源图 1232×1343），**源图不随仓库分发**：
`tools/prepare_art.py` 需要自备同规格的 PNG 底图才能重跑，仓库里只保留它的产物
（`res/drawable-nodpi/mark_figure.png`、`ic_mono.png` 与各密度磁贴图）。
原始抠图有两个问题要处理，处理链是围绕它们写的：

```
底图（看起来是透明 PNG，其实 alpha 全是 255，背景是纯白）
  ├─ 近白判背景：阈值 6，取最大连通域 → 左上角的工具栏残片、右下角的水印
  │  因为是孤立小块，直接出局，不用手工擦
  ├─ 颜色去污：抠图软件留了一圈半透明白边，先把「实心内部」的颜色按最近邻向外扩散，
  │  边缘像素改用扩散色 —— 否则放在蓝底上会泛出一圈白毛
  ├─ 软 alpha：与白色的距离当覆盖率，边缘 2px 内平滑过渡
  └─ 收边 1px + 单像素羽化                        → assets/figure-cutout.png（925 见方）
       ├─ mark_figure.png          组件与图标共用一张（512）
       │    └─ 自适应图标前景/主题单色层 = <inset 18%> 复用，不再单独出 432 的图
       └─ ic_tile_focus.png        控制中心剪影（5 档密度 × 浅深两套）
```

**这一版踩到的两个坑**（都写进脚本注释了）：

1. **量化方式**。上一版用 `FASTOCTREE` 直接压 RGBA，调色板被大片透明区吃光，
   胸口出现一条横向色带；改成「RGB 中位切分 256 色 + 保留原始 alpha」后消失，代价是多 40KB。
2. **预览图不能量化**。2×2 的渐变底压成 256 色会被切成几段宽色带，放大就是一道道横线；
   不量化又要 44KB。最后预览图改存 WebP q92，7KB 且看不出损失。

## 三种尺寸的视觉思路

| 组件 | 做法 | 为什么 |
| --- | --- | --- |
| 1×1 | 只放图形，不放文字；淡蓝底 `#F1F8FF`，图形 `match_parent + fitCenter` 撑满安全区 | 一格宽只有 60–90dp，文字一放就得 11sp 以下，两个 1×1 摆在一起还容易打架；图形本身（人/钟）已经说明了用途 |
| 2×2 | 渐变卡（`#F3F9FF→#C3DCF6`）+ 头部后方一团柔光 + 人像 `match_parent` 撑满安全区，不放文字 | 这是最"门面"的一版：110dp 最小格子里人像约 78dp，常见的 180dp 格子里能到 148dp，整块像一张小海报 |
| 4×2 | 左热区改成「人像 + 文案」横排（人像 40% 权重、高度撑满），右热区时钟竖排 | 474dp 宽的卡片里，原来的 30dp 小图标显得空；横排之后人像能到 120dp，右侧留白也被文案吃掉了 |

两个 1×1 都去掉了文字，靠图形区分：人像 = 专注，时钟 = 屏幕用时。

主色沿用插画里的蓝：强调色 `#3C82D6`（深色模式 `#8FC2F5`），桌面图标背景是同一组淡蓝渐变。

**控制中心之前为什么不显示图标**：旧版的 `ic_tile_focus.xml` 是个 `<path>` 但漏了 `fillColor`，
矢量图渲染出来是空的——所以磁贴只有文字。现在改成位图剪影，并且按深浅色各出一套：
浅色界面深墨、深色界面纯白，系统无论是否自行着色都不会「看不见」。

## 跳转逻辑

```
点击组件
  └─ PendingIntent.getActivity
       ├─ com.xiaomi.misettings/.usagestats.FocusSettingsMainActivity   ← 澎湃 OS 2/3 正常路径
       ├─ com.xiaomi.misettings/.usagestats.FocusSettingsActivity       ← 旧版类名
       ├─ com.xiaomi.misettings/.usagestats.UsageStatsMainActivity      ← 屏幕时间页（里面也有入口）
       └─ com.android.settings/.Settings                                ← 最终兜底
```

每个候选都先用 `PackageManager.getActivityInfo().exported` 校验「存在且对外导出」再跳；
全部不可用时组件会退回本应用首页并给出提示，不会出现「点了没反应」的死键。

## 符合的小米小部件规范

| 规范项 | 官方要求 | 本工程实现 |
| --- | --- | --- |
| 尺寸 | 支持 1×1 / 2×2 / 4×2 / 4×4 | 提供 1×1、2×2、4×2 三种；`minWidth/minHeight` + `targetCellWidth/Height` |
| 圆角 | 1080p 交付 55px，2K 交付 73px | `18dp`（`values-sw411dp` 下 `21dp`），按 55/3、73/3.5 换算 |
| 内容安全区 | 1080p ≥42px，2K ≥55px | 内边距 `16dp` / `18dp`（≈48px / 62px）；1×1 缩到 `12dp` / `14dp`（格子本身只有 110dp） |
| 文字 | 主信息 MiSans Demibold，次要信息 MiSans Medium 且 40% 透明度 | `sans-serif-medium`（小米设备即 MiSans）+ `#661A1C1A` / `#66F1F4F1` |
| 深色模式 | 必须适配 | `values-night` 全套色板 + 深色预览图 |
| 预览图 | 交付直角，系统裁剪 55px 圆角 | 资源内为直角 WebP q92（220×220 / 440×440 / 948×440），浅深各一套 |
| 名称 | 2~10 个汉字，且不得与应用名相同 | 应用「静叶」，组件「专注小格」「屏幕用时」「专注入口」「专注与屏幕时间」 |
| 介绍 | ≤22 个中文字符 | 「一点，直达专注模式」等，均 ≤20 字 |
| 无障碍 | 支持 TalkBack、字体放大后不截断 | 整卡一个 `contentDescription` 焦点；全部 `maxLines=1` + 省略号 |
| 禁止能力 | 不支持滑动、不支持文字输入 | 均为单点触控，无滚动、无输入 |

## 已知限制

- **时长要在系统页面里选。** 系统没有公开「带时长直接开始专注」的接口，组件只能一步把你送到那个页面（原本要 4 步）。刻意不做假按钮。
- **专注模式开了就退不出来。** 这是系统行为：到点自动结束，期间只能用相机和紧急呼叫。
- **侧载不在小米精选池。** 想出现在小米小部件中心需要企业开发者账号，按 dev.mi.com 的流程提交审核；个人自用直接装 APK 即可。
- **类名可能变。** 如果某版澎湃 OS 又改了 Activity 名，组件会退到屏幕时间页/设置页；在 `FocusLauncher.java` 的候选列表里加一行即可。

## 顺带一提：系统里还藏着一个手势入口

部分机型在 `设置 → 更多设置 → 快捷手势 → 背部轻敲` 的指令列表里，可以选到「专注模式」。
如果你的机器有这一项，那是最省事的免安装方案；没有的话（大多数版本都没有）就用这个组件。
另外澎湃 OS 3 的专注模式时长是 20–180 分钟，前 80% 时间是蓝色页面，最后 20% 转橙色。

## 点了没反应怎么办

小米默认会拦截应用之间的「链式启动」，如果组件点下去只弹一个提示或毫无反应：

1. 设置 → 应用设置 → 应用管理 → 静叶 → 权限管理 → 允许「后台弹出界面」「锁屏显示」；
2. 或在「手机管家 → 应用管理 → 权限 → 特殊权限」里给静叶放开链式启动；
3. 仍然不行的话，把 `adb logcat | grep -i "jingye\|misettings"` 的输出发我，多半是新版本改了 Activity 名。

## 工程结构

```
jingye-focus/
├── app/src/main/
│   ├── AndroidManifest.xml          # 组件、磁贴、快捷方式声明（package 由 Gradle namespace / 构建脚本注入）
│   ├── java/com/jingye/focus/
│   │   ├── FocusLauncher.java       # 跳转候选链 + 导出校验 + 兜底
│   │   ├── FocusWidgetProvider.java # 2×2 组件
│   │   ├── FocusWideWidgetProvider.java # 4×2 组件
│   │   ├── CompactWidgetProvider.java   # 1×1 组件的抽象基类
│   │   ├── FocusCompactWidgetProvider.java # 1×1 专注
│   │   ├── UsageCompactWidgetProvider.java # 1×1 屏幕用时
│   │   ├── FocusTileService.java    # 控制中心磁贴
│   │   └── MainActivity.java        # 首页：一颗按钮直达专注模式
│   └── res/                         # 布局、深色色板、矢量图标、预览图
├── tools/prepare_art.py             # 插画修复 + 抠图 + 出各尺寸图标
├── tools/gen_icons.py               # 矢量图标（时钟）
├── tools/make_previews.py           # 生成四种组件的预览图（浅色/深色）
├── tools/make_docs_assets.py        # 导出文档用素材
├── docs/                            # 预览页 preview.html、规范对照、预览配图
├── build_apk.sh                     # aapt2 → javac → d8 → zipalign → apksigner
└── gradlew / gradle/wrapper/        # Gradle Wrapper（官方分发源；国内网络慢可换腾讯云镜像）
```

构建产物不进版本库：`dist/`、`build/`、`build-manual/`、`*.apk`、`*.jks` 均已列入 `.gitignore`。

## 验证情况

**已验证**

| 项 | 方法 | 结果 |
| --- | --- | --- |
| APK 完整性 | `apksigner verify` / `unzip -t` | 通过，v3 签名，单签名者 |
| 清单与组件 | `aapt2 dump xmltree` | 4 个 widget receiver、QS tile、静态快捷方式、`queries` 均在 |
| 资源可解析 | 两条构建链各自 aapt2/AGP 链接 | 无缺失资源 |
| 构建可复现 | 手工链 + `gradlew assembleDebug` | 资源条目 88 项、dex 类 20 个完全一致 |
| 产物内容核对 | 直接解析 APK 内的 `classes.dex` / `resources.arsc` | dex 20 个类（含 9 个 `R$*` 与 2 个 lambda 合成类，业务类 8 个）、`resources.arsc` 9 个类型 88 个资源项、zip 共 47 个条目 |
| 零权限核对 | 检索二进制 `AndroidManifest.xml` 字符串池（ASCII 与 UTF-16 双编码，带阳性对照） | **无任何 `uses-permission` 元素**；无 `INTERNET` / `ACCESS_NETWORK_STATE` / `ACCESS_WIFI_STATE`。仅出现 `android.permission.BIND_QUICK_SETTINGS_TILE`，那是磁贴服务被系统绑定时要求的声明，不是向用户申请的权限 |
| 静态检查 | `gradlew lintDebug` | **0 error / 17 warning**，全部是 API 31+ 属性提示、targetSdk 落后一档这类提示 |
| 磁贴图标 | 按 5 档密度 + 浅深各一套出图，`aapt2 dump resources` 可见 10 个配置 | 改前为空路径（无 `fillColor`），改后有图 |
| 设计规范 | 对照 dev.mi.com 规范逐项核对 | 见 `docs/spec-compliance.md` |
| 预览页 | Chromium 渲染截图检查 | 排版正常，无溢出 |
| **真机 · 点击拉起** | 红米 K80 Ultra（HyperOS）实机安装后点击组件 | 能进入系统专注模式页面（不是弹提示/无响应） |
| **真机 · 组件可添加** | 长按桌面 → 添加小组件 → 全部应用 → 安卓小部件 | 四个组件均出现在列表，可拖上桌面并正常显示 |
| **真机 · 控制中心磁贴** | 下拉控制中心 → 编辑 → 添加「专注模式」 | 磁贴显示图标与文字，点击可用 |

**未覆盖**

- 其它机型与其它 HyperOS 版本下 `exported` 是否仍然成立、类名是否仍为 `FocusSettingsMainActivity`，未逐一核对；
- 不同桌面网格（4×6 / 5×7）、横屏、折叠屏下的实际留白，只在大盘上粗看过；
- 深色资源是跟随系统自动切换的（`values-night`），未逐机型核对配色对比度与文字截断。

如果别人的机器点不开，`adb logcat | grep -i "Permission Denial\|misettings"` 会直接给出原因，
按上面「点了没反应怎么办」处理即可；确认该机型系统里到底有没有「专注模式」也是第一步。

## 重新构建

```bash
# 方式一：Gradle Wrapper（已实测：Gradle 8.11.1 + AGP 8.7.3 + JDK 20）
./gradlew assembleDebug        # 产物 app/build/outputs/apk/debug/app-debug.apk
./gradlew installDebug         # 连着手机可直接装

# 方式二：不装 Android Studio / 不跑 Gradle，纯命令行
ANDROID_HOME=/path/to/android-sdk ./build_apk.sh   # 产物 dist/jingye-focus-1.0.apk
```

`build_apk.sh` 只调用 SDK 自带的 `aapt2 / javac / d8 / zipalign / apksigner`，中间文件落在 `build-manual/`；
两条链产物我已逐项比对：资源条目、dex 类列表完全一致。

国内网络拉不动 `services.gradle.org` 时，把 `gradle/wrapper/gradle-wrapper.properties` 里的
`distributionUrl` 换成 `https\://mirrors.cloud.tencent.com/gradle/gradle-8.11.1-bin.zip` 即可。

### 签名（发布必读）

`build_apk.sh` 发现 `keystore.jks` 不存在时会现场生成一份自签证书（默认口令仅供本地调试）。
**keystore 不在仓库里，也不会被提交**——它一旦泄漏，别人就能伪造你的升级包；一旦丢失，所有已装用户都无法覆盖升级。

想用自己的正式签名出包，在仓库根目录放一个 `keystore.properties`（已被 `.gitignore` 排除）：

```properties
storeFile=../keystore.jks
storePassword=********
keyAlias=jingye
keyPassword=********
```

然后在 `app/build.gradle.kts` 的 `android { }` 里新增 `signingConfigs`，并在**已有的** `release { }` 里加一行：

```kotlin
android {
    signingConfigs {
        create("release") {
            val props = java.util.Properties().apply {
                rootProject.file("keystore.properties").inputStream().use { load(it) }
            }
            storeFile = file(props.getProperty("storeFile"))
            storePassword = props.getProperty("storePassword")
            keyAlias = props.getProperty("keyAlias")
            keyPassword = props.getProperty("keyPassword")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("release")   // ← 只加这一行
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}
```

注意 `storeFile` 是相对 `app/` 模块解析的，所以 `../keystore.jks` 指向仓库根目录。

**改版本时必须同时做两件事**：`versionCode` +1，且用同一份 keystore 签名，否则老用户无法覆盖升级。

## 许可证

[MIT](LICENSE)。代码可自由使用、修改、再分发，请保留版权声明。
仓库内的插画与预览图随代码一同以 MIT 分发，但属于本项目的视觉素材，转载到其它产品时请自行替换。

