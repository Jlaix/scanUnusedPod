# scanUnusedPod

## 1、检查脚本
### 原理
使用Python开发检查脚本，原理如下：
1. 首先扫描所有工程中import的头文件，存入 allImportedFiles set 集合中；
2. 扫描工程 podspec 文件，找到所有依赖的pod名，存入 allPodNames 数组中；
3. 遍历 allPodNames 数组，根据 pod 名，和所有 pods 的存放路径，拼接得到该 pod 对应的文件路径 podPath。扫描 podPath 路径，获得路径下的所有文件，存入 filesInPod set 集合中，并判断：
 - 1. 如果 filesInPod 为空，即未搜索到 podPath 路径或 podPath 内无文件，则存入 unfindPods set 集合中；
 - 2. 如果 filesInPod 不为空，且和 allImportedFiles 的交集为空，则说明该 pod 的文件没有在工程中用到，则将该 pod 存入 unusedPods set 集合中；
4. 遍历 allPodNames 结束后，从 unusedPods 中减去白名单文件；
5. 输出 unusedPods （无用依赖 pod）与 unfindPods（未找到 pod 文件）。

### 输入参数
optional arguments:

- -h, --help            show this help message and exit
- --codes CODES [CODES ...]       传入一组项目代码文件路径
- --pods PODS [PODS ...]      传入一组 pod 代码文件路径
- --podspec PODSPEC [PODSPEC ...]     传入一组 podspec 文件路径
- --wl [WL [WL ...]]     传入白名单，白名单里的依赖不会被检测

### 【注意】
1. 如果检测到 unfindPods 较多，说明传入的 pods 存放路径可能有问题。
2. 该检查脚本仅从工程代码是否有 import pod 的文件的角度去分析，未深入分析各 pod 间的递归依赖关系，分析结果仅供参考。
 
## 2、结果
命令行输入：
  python scan_unused_dependencies.py --codes /Users/liqiyu/Work/code/DeliciousFood/Classes --pods /Users/liqiyu/Work/code/iphone-nova/Nova/Pods --podspec /Users/liqiyu/Work/code/DeliciousFood/DeliciousFood.podspec 

输出：
 - //======================= 无用依赖 ========================//
 - 总依赖 pod 59个
 - 无用依赖 pod 4个：
 - NVWebView
 - Tuan
 - YapDatabase
 - NVSound
 - 未找到 pod 文件 1个：
 - NVServices
 - 总 pod 依赖文件数：6139
 - 总无用 pod 依赖文件数：102

脚本检测出美食工程共有 59 个 Pod 依赖，其中 4 个（NVWebView、Tuan、YapDatabase、NVSound）为无用依赖，1 个（NVServices）为未找到 pod 文件。
查看 NVServices pod 后发现，该 pod 已被废弃，里面只有一个空的 README.md 文件。
