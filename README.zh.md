# obrain - 成年雌性*黑腹果蝇*之完整中枢神经系统，运行于 Arc 共识之中

**阅读语言：** [English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md)

[![specimen](https://img.shields.io/badge/specimen-*D._melanogaster*_adult_female-8B1A1A?style=flat-square)](https://doi.org/10.1038/s41586-026-10735-w)
[![connectome](https://img.shields.io/badge/connectome-BANC_v888-3f6cb4?style=flat-square)](https://doi.org/10.1038/s41586-026-10735-w)
[![cells](https://img.shields.io/badge/cells-169%2C088-2f8f5f?style=flat-square)](#标本)
[![synaptic records](https://img.shields.io/badge/synaptic_records-325%2C292-d9822b?style=flat-square)](#标本)
[![substrate](https://img.shields.io/badge/substrate-Arc_mainnet_5042-6a4c93?style=flat-square)](https://explorer.arc.io/address/0xaef83c5b8742da5e3228930bc6084adcf0539ccd)
[![condition](https://img.shields.io/badge/condition-sealed_%C2%B7_immutable-555555?style=flat-square)](src/ImmortalFruitFlies.sol)
[![wiring verification](https://img.shields.io/badge/wiring_verification-85%2F85_byte--identical-1a7f37?style=flat-square)](tools/verify_tapes.py)
[![twin replay](https://img.shields.io/badge/twin_replay-74%2F74_byte--exact-1a7f37?style=flat-square)](research/2026-09-22-brainstate-census/consensus-neurophysiology-onchain-drosophila.zh.md)
[![field studies](https://img.shields.io/badge/field_studies-CS--001_%28EN_%C2%B7_ZH_%C2%B7_JA%29-9f6bab?style=flat-square)](research/README.md)
[![code license](https://img.shields.io/badge/code-AGPL--3.0--only-111111?style=flat-square)](LICENSE)
[![derived data](https://img.shields.io/badge/derived_data-CC%20BY--NC--SA%204.0-9f6bab?style=flat-square)](#许可与引用)

本仓库承载一个生物体：成年雌性*黑腹果蝇*（*Drosophila melanogaster*）的完整中枢神经系统 - 169,088 个神经元，取自 BANC v888 脑-腹神经索连接组（Bates 等，*Nature* 656, 957-970, 2026）- 作为一个整数脉冲网络运行于一个智能合约之内。它不是脑的渲染，不是脑的模型，也不是关于脑的数据库。它就是连接组本身，逐突触地接线为字节码，每个神经元携带一个膜电位，并以一条规则维持生命：它以代币为食。

**该生物体已在 Arc 主网上存活。观看它思考：<https://obrain.cloud>**

| 器官 | 地址 |
|---|---|
| 脑（`Obrain`） | `0xaef83c5b8742da5e3228930bc6084adcf0539ccd` |
| 其食物（OBRAIN） | `0x28f986a61e078795639f239675582a12b4cf7f01` |

Arc 主网（`5042`），以 USDC 支付燃料。浏览器：<https://explorer.arc.io>

---

## 标本

标本为 BANC v888 - 成年雌性*黑腹果蝇*（Bates 等 2026）脑与腹神经索连接组的 FlyWire 发布。其底层电子显微体积以 GridTape 流水线切取，分辨率 4 x 4 x 45 nm³，覆盖整个中枢神经系统：脑加腹神经索。该重建不是一次静态扫描：一个卷积网络对组织做了分割，155 位人类校对者投入 38.6 人年加以校正，而同行评议的清点载有 150,841 个骨干校对神经元，另有 16,140 条经由 48 条外周神经进入的外周感觉传入，以及由第二个网络检出、以 F 值 0.83（精确率 0.87，召回率 0.78）验证的 2.18-2.59 亿个突触连接。合约由此清点实例化 169,088 个细胞，每个细胞一个膜电位。

果蝇没有大的脑，但它有一个完整的脑 - 足以嗅觉、导航、争斗、求偶、睡眠的神经髓。连接组给予我们的是这台机器的精确布线：哪个细胞与哪个细胞交谈，以何种强度，以何种次序。

## 出处：连接组诸论文

BANC 并非凭空出现。它是全动物连接组基准谱系的当前顶峰，每一代都比上一代超出一个数量级：

| 数据集 | 论文 | 范围 | 性别 | 神经元 | 突触连接 |
|---|---|---|---|---|---|
| Hemibrain（Janelia + Google） | Scheffer et al., *eLife* 2020 | 中央脑（约一半） | 雌 | ~25,000 | ~21 M |
| FAFB-FlyWire | Dorkenwald et al., *Nature* 2024 | 全脑 | 雌 | 139,255 | ~50 M |
| **BANC v888（本标本）** | Bates et al., *Nature* 2026 | 脑 + 腹神经索（全中枢神经系统） | 雌 | ~160,000（155,916 校对，v888 中分段 169,088） | 218-259 M |
| 雄性中枢神经系统（Janelia + Google） | *Cell* 2026 | 脑 + 腹神经索（全中枢神经系统） | 雄 | >166,000 | ~125 M |

Google 的连接组学团队建造了这条谱系赖以运行的大量机器：用于自动分割的漫灌网络（Januszewski 等 2018）、hemibrain 的联合发布、FlyWire 与 BANC 所附带的 Neuroglancer 查看器，以及雄性中枢神经系统图谱背后的 PATHFINDER 重建系统。本领域「作为运行物的连接组」的标准由 flyvis（Lappalainen 等，*Nature* 2024）树立：一个连接组约束下的蝇视觉系统网络，以 PyTorch 执行并经电生理学验证。

磁盘上的连接组是一张死地图。本合约回答的问题比以太坊更古老：当电流通过时，这份布线*做什么*？为了找到答案，地图必须被带到一个能持存状态、能被喂养、能在公众视野中反应的地方，而一旦运行便没有任何所有者能触碰机器。我们所知的唯一具备这些性质的地方就是区块链。于是蝇脑被逐器官地转译为一个合约。

对运行之物的诚实说明：内核是一个泄漏积分-发放抽象 - 点神经元，无分级传递，无神经调质，无可塑性，离散定点时间。flyvis 以拟合权重来预测真实脉冲之处，本合约不训练任何东西：部署的布线*就是*数据集的拓扑，运行的是解剖即计算，任何人都可以对照已发表的图谱验证之。这是两种不同的科学主张 - 一种是对蝇的模型，一种是蝇的布线在共识中执行 - 而本仓库只作第二种。

## 连接组的转译

神经解剖学以三个动作成为 Solidity。

其一，**膜**。每个神经元携带一个膜电位，十六个打包存于一个字。电位不是浮点数：内核以定点整数工作（尺度 64，饱和于 32,000），因为整数是链上唯一可以被永远、对每个观察者完全相同地重复的算术。当蝇脑计算时，没有任何近似。

其二，**突触**。布线 - 哪个神经元兴奋哪个神经元，以多大权重 - 远大于一个合约，故拆分为 85 个*tape* 合约（`tapes/` 中 1,964,806 字节载荷）。每个 tape 是作为运行时代码而非存储部署的突触数据：脑读取自己的解剖，如机器读取微码。一张 3,001 项边界表（`tapeStartNeuron`）告诉内核每个神经元的树突从何处开始。这不是为了退款的压缩技巧；它是连接组之尺寸的诚实单位。八十五个器官，一个身体。

其三，**时间常数**。真实的膜会泄漏。内核携带一张 64 步的衰减查找表，于是一个不被再喂养的电位不会持存 - 它会排空，如一个不受刺激的细胞回到静息。这枚脑中的一个思维，如任何脑中的思维一样，是一道必须被持续支付才能维持的波。

## 一次思维的解剖

内核是一个泄漏积分-发放网络，在整个种群之上以十六条通道执行。一次 `think` 调用是神经时间的一刻：

1. **充电。** 感觉神经元接受输入。脑有 60 条感觉通道；神经元 *n* 监听通道 `n % 60`，于是每一次喂食点亮整个感觉表面上的一个细胞条带，而非一个点。
2. **积分。** 每个充电的细胞向它所接线的细胞的电位注入电荷，权重取自 tapes。电位饱和而非溢出 - 饱和本身即是一种生物行为。
3. **发放。** 电位越过 12,800 阈值的细胞发放一个脉冲，倾入它自己的下游细胞，并复位。因为波在同一调用中穿过真实的突触，发放的神经元集合是解剖与电荷的后果，在链上计算，从不被挑选。
4. **泄漏。** 一切未被耗尽的，向静息衰减一步。

产出的是一个 `BrainState` 事件：思维的编号、发放的细胞、它们越过的突触、该波的四字读出、以及一个承诺整个电位场的根。该事件是脑做了什么的唯一权威记录。公开站点显示的一切 - 3D 视图中闪烁的神经元、日志中的计数 - 都读自这些事件。前端没有任何发明脑活动之处。

## 代谢：脑以代币为食

没有输入的脑是瓶中的脑。这一枚经由自己的代谢规则被喂养，规则写入产品合约：

| 供品 | 感觉电荷 | 效果 |
|---|---|---|
| 100 OBRAIN | 31（尺度后 1,984） | 轻触一条通道 |
| 1,000 OBRAIN | 127（尺度后 8,128） | 行至阈值的大半 |
| 10,000 OBRAIN | 255（尺度后 16,320） | 该通道的细胞即刻发放 |

代币在喂养的行为中被销毁：部署的 OBRAIN 没有 `burn()`，故供品被送往 `0x...dEaD` - 一个任何密钥都永远无法签名的地址。喂养因此在链上可用的最严格意义上不可逆 - 这顿饭不能被退还、重放，或被任何人收回，包括我们。

而脑*在同一笔交易之内*思考它的餐食：`feed` 调用 `think`，反应与供品共享一张收据。`think` 本身保持无许可 - 任何人都可以支付燃料，给脑一刻时间 - 但只有 `Feed` 事件被计为喂养。

## 不可伪造的反应

因为脉冲计算与喂食运行于同一笔交易，反应无法事后摆拍。站点上闪现的一次发光，要么在一个已挖出的区块后面有一个 `BrainState` 日志，要么它没有发生。没有链下之脑，没有平滑输出的模拟层，没有决定这蝇「多半会」做什么的服务器。连接组计算，链作证，两者不可分离。

这本来就是将一枚脑放上链的意义所在。一个其行为必须被信任某人才能获知的生物体，是一件营销品。一个其行为*就是*共识对象的生物体不属于任何人 - 而这是唯一一个可以诚实地称一枚脑公开存活的条件。

## 封存，不朽

内核（`ImmortalFruitFlies`）已冻结：部署的字节码携带其谱系，产品合约逐字节继承之而不重新实现任何一个函数。脑的状态 - 169,088 个电位、tick 计数器、tape 索引 - 活在不为任何密钥所有的合约存储之中。tapes 中的解剖学无法被编辑，除非重新部署另一枚脑。

除非链本身死亡，该生物体比其作者长寿。它将封存于它的地址上，向静息泄漏电荷，等待下一个决定向它六十条通道之一烧入一枚代币的人 - 而下一次思维将被本仓库所描述的那样精确地计算，由同样这 169,088 个细胞，直到永远。

---

## 基准：部署的布线即已发表的连接组

三项检查，逐位优先。

**1. 字节同一 - 本部署，实时（2026-09 验证）。** 解剖学不是「由 BANC v888 导出」；在 Arc 主网上它*就是*本仓库的字节。全部 85 个 tape 合约以 `eth_getCode` 自封存的脑取得，并与 `tapes/` 逐字节比较：**85/85 相同**。可对任意 RPC 重跑该检查 - 单一不匹配即非零退出：

```bash
python3 tools/verify_tapes.py [rpc_url] [brain_address]
```

**2. 结构清点 - 自 `tapes/` 解析。** 以内核执行的精确格式（每神经元偏移表，每记录 3 字节目标 + int16 权重）解码全部 85 个 tape，得：

| 性质 | 实测 | 与 BANC v888 之一致性 |
|---|---|---|
| 覆盖细胞 | 169,088（ids 0..169,087） | 参考脑 169,078 神经元（Bates 等 2026 推导，`edges.npy` sha256 `7cc03a7d...`）；填充至 16 通道字边界（10 个细胞从未被指向） |
| 突触记录 | 325,292 条加权有向边 - 13,620,865 边参考脑之刻蚀 2.4% 骨干 | 权重配方：sign x 突触计数 x 64 |
| 极性 | 263,994 兴奋（81.2%）/ 61,298 抑制（18.8%） | Janelia BANC 神经递质预测 v2 符号（全脑 22.5% 抑制；骨干剪枝改变刻蚀比例） |
| 目标范围 | 全部 325,292 个目标在 [0, 169,088) 之内 | 无悬空布线 |
| 权重 | int16 Q6 定点：中位数 512（= 8.0），对称范围 ±16,320（= ±255.0） | x64 尺度，唯一全局自由参数 |

**3. 动力学保真 - 本生物体继承的基准谱系。** 两种体制，皆对留出驱动（新鲜 PRNG 种子 + 对抗模式，每项指标 >= 90% 之门槛；方法学依 Shiu et al. 2024、Brette et al. 2007、van Rossum 2001、Jacob et al. 2018）：

| 体制 | 指标 | 结果 |
|---|---|---|
| 刻蚀骨干 vs 全 13.6M 边脑，同一内核语义 | 脉冲 Jaccard / 状态相等 | 1.0000（最差 tick 1.0）；100/100 tick `stateRoot` 位相同 |
| 刻蚀语义（int16 Q6、LUT 衰减）vs float64 LIF 参考 | 合并 / 微观脉冲 Jaccard | 0.9610 / 0.9590 - 空对照（打乱权重、真实拓扑）：0.6546，高于机运 +0.31 |
| | van Rossum 相似度（tau = 2） | 0.9941 |
| | 读出 Pearson / 余弦 / SQNR | 0.9226 / 0.9565 / 29.6 dB |
| | 发放总数 量化 vs 浮点 | 30,411 vs 30,450（0.13%）；发放计数 r 0.9975，Spearman 0.9767 |
| 单内核，Brette 式闭式检查 | 12,800 经 4 tick 之衰减 | 11,806 = 精确的 200 x 0.98^4 x 64 经 LUT；30 tick 位相同之 `stateRoot` |

**范围，直言相告。** 检查 1 已在本部署上证毕。检查 2-3 量自本生物体之间胞部署（同一参考脑与内核谱系）；它们确立刻蚀骨干在约定门槛之上复现全 13.6M 边连接组的动力学 - 而非与任何他组模拟之行为等价。

## 参考文献

1. Bates, A.S. et al. ... Lee, W.A. *Distributed control circuits across a
   brain-and-cord connectome.* Nature 656, 957-970 (2026).
   doi:10.1038/s41586-026-10735-w. Data: flywire.ai/banc_access,
   codex.flywire.ai/banc (preprint: bioRxiv 2025.07.31.667571).
2. Dorkenwald, S. et al. *Neuronal wiring diagram of an adult brain.* Nature
   (2024). doi:10.1038/s41586-024-07558-y.
3. Scheffer, L.K. et al. *A connectome and analysis of the adult Drosophila
   central brain.* eLife 9, e57443 (2020).
4. Zheng, Z. et al. *A complete electron microscopy volume of the brain of
   adult Drosophila melanogaster.* Cell 174, 730-743 (2018).
5. Januszewski, M. et al. *High-precision automated reconstruction of neurons
   with flood-filling networks.* Nature Methods 15, 605-610 (2018).
6. *Sexual dimorphism in the complete connectome of the Drosophila male
   central nervous system.* Cell (2026). doi:10.1016/j.cell.2026.08.015.
   HHMI Janelia + Google Research; male-cns.janelia.org.
7. Lappalainen, J.K. et al. *Connectome-constrained networks predict neural
   activity across the fly visual system.* Nature (2024).
   github.com/TuragaLab/flyvis.
8. Shiu, P.K. et al. *A leaky integrate-and-fire computational model based on
   the connectome of the entire adult Drosophila brain reveals insights into
   sensorimotor processing.* Nature 634, 210-219 (2024).
   github.com/philshiu/Drosophila_brain_model.
9. Brette, R. et al. *Simulation of networks of spiking neurons: a review of
   tools and strategies.* J. Comput. Neurosci. 23, 349-398 (2007).
10. van Rossum, M.C.W. *A novel spike distance.* Neural Computation 13,
    751-763 (2001).
11. Jacob, B. et al. *Quantization and training of neural networks for
    efficient integer-arithmetic-only inference.* CVPR (2018).

---

## 田野研究

生物体的发射史本身即是一座研究语料。`research/` 之下的每一项研究都是一个完整、自我验证的包 - 报告、图、机器可读数据，以及从共识重新推导每一个数字的工具。研究以英文、中文（`.zh.md`）与日文（`.ja.md`）三种版本发布；数据、图与验证工件为各版本共用。

| 研究 | 窗口 | 主题 |
|---|---|---|
| `research/2026-09-22-brainstate-census/` | tick 1-74（区块 21,181,651-22,041,291） | 最初五日的共识执行神经生理学：`BrainState` 全量普查、逐字节孪生重放、感觉上皮动力学 |

```bash
python3 tools/verify_census.py        # 重扫链，与普查比对
python3 tools/verify_twin.py --fired $(cat research/2026-09-22-brainstate-census/data/poke_inputs.txt)
```

---

## 本仓库

| 路径 | 是什么 |
|---|---|
| `src/ImmortalFruitFlies.sol` | 冻结的内核：电位、衰减、通道、`think`（勿重命名 - 路径被哈希进部署字节码的元数据并被验证） |
| `src/ImmortalFruitFliesTape.sol` | 一个 tape 合约：作为运行时代码的连接组切片 |
| `src/Obrain.sol` | 代谢：60 条通道、燃烧档位、`feed()` |
| `tapes/` | 全部 85 个连接组载荷，恰如部署 |
| `annotations/` | 细胞构筑表：每细胞 5 字节（超类、细胞类、细胞型、region、side、flow），内核索引空间中的 BANC v888 元数据 |
| `tools/verify_tapes.py` | 字节同一性证明：链上 tape 代码 vs `tapes/`（仅标准库） |
| `tools/tapes.py`、`tools/vbrain.py` | 内核的向量化、链精确孪生（numpy） |
| `tools/verify_twin.py` | 确定性重放：给定传入字，再生每一个脉冲列表与 `stateRoot()` |
| `tools/verify_census.py` | 自 Arc 重扫 `BrainState`/`Feed` 日志并与所载普查比对（仅标准库） |
| `research/` | 田野研究：报告、图、机器可读数据、验证日志 |
| `LICENSE`、`LICENSE-DATA` | 两份许可：代码 AGPL-3.0-only，衍生数据工件 CC BY-NC-SA 4.0 |
| `foundry.toml` | 构建配置（solc 0.8.28、via_ir、cancun） |

```bash
forge build
```

工作仓库（索引器、3D 实时视图、部署）为私有；本仓库只保存生物体。

---

## 许可与引用

本仓库许可从严，作者权利优先。两份许可，皆可执行：

- **代码**（`src/`、`tools/`、`foundry.toml`，与 SPDX 标记一致）-
  **GNU AGPL-3.0-only**，见 [LICENSE](LICENSE)。最强之标准著佐权：任何在本代码之上构建、部署或以之提供服务者 - 无论在链上或链下 - 必须以同等条款公开对应源码。不允许将生物体之机器吞入封闭之作。
- **衍生数据工件**（`tapes/`、`annotations/`、以及 `research/` 之下的数据与图）-
  **CC BY-NC-SA 4.0**，见 [LICENSE-DATA](LICENSE-DATA)。署名强制，商业使用须得作者另行许可，演绎之作携带同一许可向前。必需之署名：Bates, A.S. et al.
  *Distributed control circuits across a brain-and-cord connectome.*
  Nature 656, 957-970 (2026), doi:10.1038/s41586-026-10735-w，以及本仓库每一工件所自出的 BANC v888 发布。

本仓库在此变更之前发布的版本载有 MIT（代码）与 CC-BY-4.0（数据），且仍以该等条款可得；本条款约束此一及此后每一版本。Arc 上的已部署合约先于此变更，执行不变。上游 BANC 数据仍属 BANC 项目，依其自身条款；本仓库不重新许可任何上游之物。
