# Complete R8 — independent mechanism and proof audit

**审阅对象：** `revision/econometrica-r8-full-response-2026-09-17`，提交 `be77b2a81b4d3a68806c534c1e892d2eb4b1230d`。  
**本轮建议：Reject in its present form。** 这是用户委托、参照 Econometrica 标准的独立咨询性审稿，不是期刊正式审稿或编辑决定。

[阅读完整 referee report](referee_report.md)。报告不将已经修复的问题重新列为错误，也没有发现主上界定理的反例。核心反对意见是：有效的有限模型计算证书，尚未与足够有说服力的动态经济学机制连成一体。

## 本轮新增判断与证据

两阶段稳健定理在整个已声明参数族上满足 `theta_plus < 0 < theta_minus`；历史动态审稿记录中的两个初始最优调整则都为正上限。报告给出解析推导，并明确这不是对两阶段定理的反例，而是两类经济机制之间仍缺桥梁。

新增退约罚则分析给出值函数的包络性质和恢复原强制运行价值的充分罚则界，说明该合同问题可以直接放入现有认证框架。退约权、初始持仓权限的动态数值则引用上一轮已落盘结果，**不冒称本轮重新求解**。

独立程序通过 24 个有理数小型 MDP、48 个模型—区间组合上的 4,152 项精确不等式检查和 3,240 项参数点排序链；另以 65 位 Decimal 精度检查 27 个两阶段参数组合及越界 tilt 反例。所有检查通过。精确有理数测试不等于一般定理证明；Decimal 结果也不是向外舍入的区间证明。

## 文件与复现

- `referee_report.md`：完整英文报告、问题分级、既有修复的处置及下一轮科学闭合条件。
- `reviewer_checks.py`：无网络、无作者代码导入、仅 Python 标准库的独立检验程序。
- `reviewer_results.json`：本轮真实运行结果摘要，含脚本 SHA-256、环境、设计和未执行事项。
- `source_inventory.json`：审阅提交、历史上下文、已读取源码的 Git blob 身份与范围说明。

从仓库根目录运行（Python 3.11 或更新版本）：

```bash
python reviews/2026-09-17-econometrica-r8-independent-mechanism-audit/reviewer_checks.py \
  --out /tmp/nbo-r8-independent-results.json
```

运行记录使用 Python 3.13.5。结果不包含计时；不同解释器版本会改变环境字段，科学计数和数值应分别比较。

## 版本及范围

本轮检查时，`revision/econometrica-r9-contract-response-2026-09-17` 仍指向上一轮 R8 review 的 `8c20474bca5b7388f5ba4640ec165f1ad8f5e91a`，没有新的 R9 科学稿件。因此本报告针对实际最新完整稿 R8，不是假称审阅了 R9。

本分支基于上述历史 review 提交，新内容仅放在本目录。不修改主稿、历史报告、复制实验源码或数值输入。本轮未重新运行作者的完整 1,568-action 动态实验、神经训练、财富网格实验，未重新编译或视觉检查 PDF，也未建立 diffusion 或 transition-constructor 误差包络。报告逐项区分新执行证据、解析推导和引用的历史观察。
