# coding=utf-8

import codecs, os
import os
import argparse
import sys
import re

scanCodePaths = []  # 搜索代码路径
scanPodPaths = []   # 搜索 Pod 代码路径
podspecPaths = []   # podspec 文件路径
scanExtension = ['.h', '.m', '.pch']
whiteList = set()


#===== 遍历文件或文件行的工具方法 =====
def travelPath(path, *extensions):
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            fullPath = os.path.join(dirpath, filename)
            (_, extension) = os.path.splitext(filename)
            if not all(extensions) or not len(extensions):
                yield fullPath
            elif os.path.exists(fullPath) and extension in extensions:
                yield fullPath

def getFilename(path, *extensions):
    if os.path.isfile(path):
        yield path
    elif os.path.isdir(path):
        for filePath in travelPath(path, *extensions):
            yield filePath
    else:
        print('path wrong: %s' % path)

def readFile(path, *extensions):
    for filename in getFilename(path, *extensions):
        with codecs.open(filename, 'r', 'utf-8', errors='replace') as file:
            yield (file.readlines(), filename)

def readLine(path, *extensions):
    for lines, filename in readFile(path, *extensions):
        for line in lines:
            yield (line, filename)


#===== 提取文件名、依赖pod、import文件等信息的方法 =====
def getFileNames(path, *scanExtension):
    for fileName in travelPath(path, *scanExtension):
        yield fileName

def getDependenciedPodNames(paths):
    # 匹配依赖的 pod 名
    pattern = re.compile('.*?s.dependency.*?[\'\"](.*?)[\'\"].*?')
    for path in paths:
        for line, filename in readLine(path, ['.podspec']):
            matched = pattern.match(line)
            if matched:
                # 若为路径，如“SAKStatistics/Core”，截取一级目录 SAKStatistics 作为 pod name
                podPath = re.split(r'[\s\/]+', matched.group(1))
                yield podPath[0]

def getImportedFiles(paths, *scanExtension):
    # 匹配所有 import 了的文件名
    pattern = re.compile('(.*?)#import.*?[\'\"<](.*?)[\'\">].*?')
    for path in paths:
        for line, filename in readLine(path, *scanExtension):
            matched = pattern.match(line)
            if matched and not '//' in matched.group(1):
                yield matched.group(2)


#===== 扫描无用Pod依赖方法 =====
def scanUnusedDependencies():
    global scanCodePaths, scanPodPaths, podspecPaths, scanExtension, whiteList
    
    # 所有项目中引入的头文件
    allImportedFiles = {os.path.splitext(os.path.basename(fileName))[0] for fileName in getImportedFiles(scanCodePaths, *scanExtension)}

    # 所有依赖的 Pod
    allPodNames = [podName for podName in getDependenciedPodNames(podspecPaths)]

    unusedPods = set()
    unusedPodFileCount = 0
    totalPodFileCount = 0
    unfindPods = set()
    for podName in allPodNames:
        for scanPodPath in scanPodPaths:
            podPath = os.path.join(scanPodPath, podName)

            # pod 的各个文件
            filesInPod = {os.path.splitext(os.path.basename(fileName))[0] for fileName in getFileNames(podPath, *scanExtension)}
            totalPodFileCount += len(filesInPod)

            if not filesInPod:
                unfindPods.add(podName)
            elif not allImportedFiles & filesInPod:
                # 两者无交集，则 pod 是无用依赖
                unusedPods.add(podName)
                unusedPodFileCount += len(filesInPod)
            
    unusedPods -= whiteList # 白名单 

    if unusedPods:
        print '//======================= 无用依赖 ========================//'
        print '总依赖 pod ' + str(len(allPodNames)) + '个'
        print '无用依赖 pod ' + str(len(unusedPods)) + '个：'
        for pod in unusedPods:
            print pod
        print '未找到 pod 文件 ' + str(len(unfindPods)) + '个：'
        for pod in unfindPods:
            print pod
        print '总 pod 依赖文件数：' + str(totalPodFileCount)
        print '总无用 pod 依赖文件数：' + str(unusedPodFileCount)
    else:
        print "恭喜~~ 没有无用pod依赖！"

def parseParams(arguments):
    parser = argparse.ArgumentParser(description='检测 podspec 无用依赖')
    parser.add_argument('--codes', nargs='+', help='传入一组项目代码文件路径')
    parser.add_argument('--pods', nargs='+', help='传入一组 pod 代码文件路径')
    parser.add_argument('--podspec', nargs='+', help='传入一组 podspec 文件路径')
    parser.add_argument('--wl', nargs='*', help='传入白名单，白名单里的依赖不会被检测')
    
    args = parser.parse_args(arguments)
    return args

def main():
    global scanCodePaths, scanPodPaths, podspecPaths, whiteList
    
    arguments = parseParams(sys.argv[1:])
    scanCodePaths = arguments.codes
    scanPodPaths = arguments.pods
    podspecPaths = arguments.podspec
    if arguments.wl:
        whiteList = set(arguments.wl)
    scanUnusedDependencies()


if __name__ == '__main__':
    main()

