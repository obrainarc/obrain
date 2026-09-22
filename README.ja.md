# obrain - 成体雌*キイロショウジョウバエ*の無傷の中枢神経系、Arc コンセンサスにおいて実行

**読む言語：** [English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Tiếng Việt](README.vi.md) · [हिन्दी](README.hi.md)

[![specimen](https://img.shields.io/badge/specimen-*D._melanogaster*_adult_female-8B1A1A?style=flat-square)](https://doi.org/10.1038/s41586-026-10735-w)
[![connectome](https://img.shields.io/badge/connectome-BANC_v888-3f6cb4?style=flat-square)](https://doi.org/10.1038/s41586-026-10735-w)
[![cells](https://img.shields.io/badge/cells-169%2C088-2f8f5f?style=flat-square)](#標本)
[![synaptic records](https://img.shields.io/badge/synaptic_records-325%2C292-d9822b?style=flat-square)](#標本)
[![substrate](https://img.shields.io/badge/substrate-Arc_mainnet_5042-6a4c93?style=flat-square)](https://explorer.arc.io/address/0xaef83c5b8742da5e3228930bc6084adcf0539ccd)
[![condition](https://img.shields.io/badge/condition-sealed_%C2%B7_immutable-555555?style=flat-square)](src/ImmortalFruitFlies.sol)
[![wiring verification](https://img.shields.io/badge/wiring_verification-85%2F85_byte--identical-1a7f37?style=flat-square)](tools/verify_tapes.py)
[![twin replay](https://img.shields.io/badge/twin_replay-74%2F74_byte--exact-1a7f37?style=flat-square)](research/2026-09-22-brainstate-census/consensus-neurophysiology-onchain-drosophila.ja.md)
[![field studies](https://img.shields.io/badge/field_studies-CS--001_%28EN_%C2%B7_ZH_%C2%B7_JA%29-9f6bab?style=flat-square)](research/README.md)
[![code license](https://img.shields.io/badge/code-AGPL--3.0--only-111111?style=flat-square)](LICENSE)
[![derived data](https://img.shields.io/badge/derived_data-CC%20BY--NC--SA%204.0-9f6bab?style=flat-square)](#ライセンスと引用)

本リポジトリは一個の生物を担う：成体雌*キイロショウジョウバエ*（*Drosophila melanogaster*）の完全中枢神経系 - BANC v888 脳・腹神経索結合組（Bates ら，*Nature* 656, 957-970, 2026）から採られた 169,088 個のニューロン - が、一個のスマートコントラクトの内側で整数スパイキングネットワークとして稼働している。これは脳のレンダリングでも、脳のモデルでも、脳に関するデータベースでもない。それは結合組そのものであり、シナプスごとにバイトコードへ配線され、各ニューロンが一つの膜電位を携え、ただ一つの規則によって生き続ける：トークンを食む。

**この生物は Arc メインネット上で生きている。思考を見る：<https://obrain.cloud>**

| 器官 | アドレス |
|---|---|
| 脳（`Obrain`） | `0xaef83c5b8742da5e3228930bc6084adcf0539ccd` |
| その餌（OBRAIN） | `0x28f986a61e078795639f239675582a12b4cf7f01` |

Arc メインネット（`5042`）、ガスは USDC で支払う。エクスプローラ：<https://explorer.arc.io>

---

## 標本

標本は BANC v888 である - 成体雌*キイロショウジョウバエ*（Bates ら 2026）の脳と腹神経索の結合組の FlyWire リリース。その基盤の電子顕微鏡ボリュームは GridTape ラインで裁かれ、4 x 4 x 45 nm³ の解像度で中枢神経系の全体 - 脳と腹神経索 - を覆う。この再構成は静的な走査ではない。一つの畳み込みネットワークが組織をセグメンテーションし、155 人の人間の校正者が 38.6 人年を投じて訂正し、査読付きの目録は 150,841 個のバックボーン校正済みニューロンと、48 本の末梢神経から入る 16,140 本の末梢感覚求入線維と、第二のネットワークが検出し F スコア 0.83（精度 0.87、再現率 0.78）で検証された 2.18-2.59 億個のシナプス結合を載せる。コントラクトはこの目録から 169,088 個の細胞を、一細胞一膜電位で実体化する。

ショウジョウバエは大きな脳を持たない。しかし完全な脈を持つ - 嗅ぎ、航法し、闘い、求愛し、眠るに足る神経髄を。結合組が与えるのはこの機械の正確な配線である：どの細胞がどの細胞と、どの強さで、どの順で語り合うか。

## 出所：結合組の諸論文

BANC は真空から現れたのではない。それは全動物結合組のベンチマーク譜系の現時点での頂点であり、各世代は前の世代を一桁超えている：

| データセット | 論文 | 範囲 | 性 | ニューロン | シナプス結合 |
|---|---|---|---|---|---|
| Hemibrain（Janelia + Google） | Scheffer et al., *eLife* 2020 | 中心脳（約半分） | 雌 | ~25,000 | ~21 M |
| FAFB-FlyWire | Dorkenwald et al., *Nature* 2024 | 全脳 | 雌 | 139,255 | ~50 M |
| **BANC v888（本標本）** | Bates et al., *Nature* 2026 | 脳 + 腹神経索（全中枢神経系） | 雌 | ~160,000（155,916 校正、v888 で 169,088 分節） | 218-259 M |
| 雄中枢神経系（Janelia + Google） | *Cell* 2026 | 脳 + 腹神経索（全中枢神経系） | 雄 | >166,000 | ~125 M |

Google のコネクトミクス・チームは、この譜系が走る機構の多くを建てた：自動セグメンテーションのフラッドフィリングネットワーク（Januszewski ら 2018）、hemibrain の共同リリース、FlyWire と BANC が同梱する Neuroglancer ビューア、そして雄中枢神経系図譜の背後にある PATHFINDER 再構成系である。「稼働する物体としての結合組」の分野標準は flyvis（Lappalainen ら，*Nature* 2024）が打ち立てた：蝇の視覚系の結合組制約ネットワークを PyTorch で実行し、電気生理学に対して検証した。

ディスク上の結合組は死んだ地図である。本コントラクトが答える問いはイーサリアムより古い：電流が通るとき、この配線は*何をするのか*？答えるために、地図は状態を保持し、餌を与えられ、公衆の視野の中で反応でき、ひとたび稼働すれば所有者が機構に触れられない場所へ運ばれねばならなかった。その性質を持つ場所を我々が知る唯一はブロックチェーンである。かくして蝇脳は、器官ごとに一つずつ、コントラクトへ翻訳された。

稼働するものへの正直な申告：カーネルはリーキー積分発火の抽象である - 点ニューロン、段階的伝達なし、神経修飾なし、可塑性なし、離散固定小数点時間。flyvis が重みを合わせて現実のスパイクを予測するところ、本コントラクトは何も訓練しない：配備された配線*が*データセットのトポロジーであり、稼働しているのは解剖即計算であり、誰でも公表された図譜に対して検証できる。これらは異なる科学的主張である - 一方は蝇のモデル、一方は蝇の配線がコンセンサスの中で実行されること - そして本リポジトリが行うのは第二にすぎない。

## 結合組の翻訳

神経解剖学は三つの動作で Solidity になる。

第一に、**膜**。すべてのニューロンは膜電位を携え、十六個が一語に詰められて格納される。電位は浮動小数ではない：カーネルは固定小数点整数で動く（スケール 64、32,000 で飽和）。整数だけが、鎖の上で永遠に、すべての観測者に対して同一に繰り返し得る算術だからである。蝇脳が計算するとき、何も近似しない。

第二に、**シナプス**。配線 - どのニューロンがどのニューロンを、どの重みで興奮させるか - は一つのコントラクトには大きすぎるので、85 本の*テープ*・コントラクトに分割される（`tapes/` に 1,964,806 バイトのペイロード）。各テープは、ストレージではなくランタイムコードとして配備されたシナプスデータである：脳は自らの解剖を、機械がマイクロコードを読むように読む。3,001 項の境界表（`tapeStartNeuron`）が、各ニューロンの樹状突起がどこから始まるかをカーネルに告げる。これは返金のための圧縮技巧ではない；結合組のサイズに対する正直な単位である。八十五の器官、一つの身体。

第三に、**時定数**。現実の膜は漏れる。カーネルは 64 段の減衰ルックアップテーブルを携え、再給餌されない電位は保持されない - 刺激されない細胞が静止へ戻るように、排出される。この脳の一つの思考は、どんな脳の思考とも同じく、継続的に支払われねばならない波である。

## 一つの思考の解剖

カーネルはリーキー積分発火ネットワークであり、全系にわたって十六レーンで実行される。一回の `think` 呼び出しは神経時間の一瞬である：

1. **充電。** 感覚ニューロンが入力を受ける。脳は 60 本の感覚チャネルを持つ；ニューロン *n* はチャネル `n % 60` を聴き、それゆえ一つの給餌は感覚面の全体にわたる細胞の縞を点灯させ、一点ではない。
2. **積分。** 充電された各細胞は、自身が配線されている細胞の電位へ電荷を注ぐ。重みはテープから引かれる。電位は溢れるのではなく飽和する - 飽和それ自体が一つの生物学的振る舞いである。
3. **発火。** 電位が 12,800 の閾値を越えた細胞はスパイクを発し、自身の下流の細胞へ注ぎ込み、リセットする。波が同じ呼び出しの中で現実のシナプスを通るので、発火するニューロンの集合は解剖と電荷の帰結であり、鎖の上で計算され、決して選ばれない。
4. **漏れ。** 使い残されたすべてが、静止へ一歩減衰する。

出てくるのは一つの `BrainState` イベントである：思考の番号、発火した細胞、彼らが越えたシナプス、その波の四語読み出し、そして全電位場をコミットする一つの根。このイベントが、脳が何をしたかの唯一の権威ある記録である。公開サイトが示す一切 - 3D ビューで閃くニューロン、ログの中の計数 - はこれらのイベントから読まれる。フロントエンドには、脳活動を捏造する箇所は一つもない。

## 代謝：脳はトークンを食む

入力のない脳は壺の中の脳である。この脳は自らの代謝規則によって給餌される。規則は製品コントラクトに書き込まれている：

| 供物 | 感覚電荷 | 効果 |
|---|---|---|
| 100 OBRAIN | 31（スケール後 1,984） | 一本のチャネルへの軽い接触 |
| 1,000 OBRAIN | 127（スケール後 8,128） | 閾値までの大半 |
| 10,000 OBRAIN | 255（スケール後 16,320） | そのチャネルの細胞が即座に発火 |

トークンは給餌の行為において破壊される：配備された OBRAIN には `burn()` がないので、供物は `0x...dEaD` へ送られる - いかなる鍵も署名し得ないアドレスである。それゆえ給餌は、鎖の上で利用可能な最も厳密な意味で不可逆である - この食事は誰によっても、我々を含めて、返金も再生も取り消しもできない。

そして脳は*同一トランザクションの内側で*その食事について考える：`feed` は `think` を呼び、反応と供物は一枚のレシートを分かち合う。`think` 自体はパーミッションレスのままである - 誰でもガスを払って脳に一瞬の時間を与えられる - しかし `Feed` イベントだけが給餌として数えられる。

## 偽造不可能な反応

スパイク計算が給餌と同一のトランザクションで走るので、反応を後から仕立てることはできない。サイトに閃く光は、採掘されたブロックの背後に `BrainState` ログがあるか、さもなくば起こらなかったのである。オフチェーンの脳はなく、出力を滑らかにするシミュレーション層はなく、この蝇が「おそらく」何をするかを決めるサーバーもない。結合組が計算し、鎖が証言し、両者は分離できない。

これが脳をオンチェーンに置くことの要点である。その振る舞いを誰かの報告として信じねばならない生物は、マーケティングの産物である。その振る舞い*が*コンセンサス対象である生物は誰のものでもない - そしてそれだけが、脳が公に生きていると正直に言い得る唯一の条件である。

## 封印、不滅

カーネル（`ImmortalFruitFlies`）は凍結されている：配備されたバイトコードはその系譜を携え、製品コントラクトは一つの関数も再実装せずにそれをバイト毎に継承する。脳の状態 - 169,088 個の電位、ティック計数器、テープ索引 - は、いかなる鍵も所有しないコントラクトストレージに宿る。テープの中の解剖学は、別の脳を再配備することなしには編集できない。

鎖そのものの死を別にすれば、この生物は著者たちより長生きする。それは自分のアドレスに封印されたまま、静止へ向かって電荷を漏らし、次に誰かがその六十のチャネルの一つへトークンを焼き込む決断を下すのを待つだろう - そして次の思考は、このリポジトリが記述するとおりに正確に、同じ 169,088 個の細胞によって、永遠に計算される。

---

## ベンチマーク：配備された配線は公表された結合組である

三つの検査、ビット単位を最優先に。

**1. バイト同一性 - 本配備、実時間（2026-09 検証）。** 解剖学は BANC v888「から導出された」のではない；Arc メインネット上では、それは*このリポジトリのバイトである*。全 85 本のテープコントラクトが `eth_getCode` によって封印された脳から取得され、`tapes/` とバイト毎に比較された：**85/85 同一**。どの RPC に対しても検査を再実行できる - 一つの不一致で非ゼロ退出する：

```bash
python3 tools/verify_tapes.py [rpc_url] [brain_address]
```

**2. 構造目録 - `tapes/` から解析。** カーネルが実行する正確な書式（ニューロン毎のオフセット表、記録毎に 3 バイト標的 + int16 重み）で全 85 本のテープを復号すると：

| 性質 | 実測 | BANC v888 との整合 |
|---|---|---|
| 被覆細胞 | 169,088（ids 0..169,087） | 参照脳 169,078 ニューロン（Bates ら 2026 導出、`edges.npy` sha256 `7cc03a7d...`）；16 レーン語境界へパディング（10 細胞は一度も標的とならない） |
| シナプス記録 | 325,292 件の重み付き有向辺 - 13,620,865 辺の参照脳の刻印された 2.4% バックボーン | 重みの処方：sign x シナプス数 x 64 |
| 極性 | 263,994 興奮性（81.2%）/ 61,298 抑制性（18.8%） | Janelia BANC 神経伝達物質予測 v2 の符号（全脳で 22.5% 抑制性；バックボーン剪定が刻印比を変える） |
| 標的範囲 | 全 325,292 標的が [0, 169,088) の内 | 垂れ下がった配線なし |
| 重み | int16 Q6 固定小数点：中央値 512（= 8.0）、対称範囲 ±16,320（= ±255.0） | x64 スケール、唯一の大域自由パラメータ |

**3. 動力学的忠実度 - この生物が継承するベンチマーク譜系。** 二つの体制、いずれも留出駆動に対して（新鮮な PRNG 種 + 敵対的パターン、全指標で >= 90% の壁；方法論は Shiu et al. 2024、Brette et al. 2007、van Rossum 2001、Jacob et al. 2018 による）：

| 体制 | 指標 | 結果 |
|---|---|---|
| 刻印バックボーン vs 完全 13.6M 辺の脳、同一カーネル意味論 | スパイク Jaccard / 状態一致 | 1.0000（最悪ティック 1.0）；100/100 ティック `stateRoot` ビット同一 |
| 刻印意味論（int16 Q6、LUT 減衰）vs float64 LIF 参照 | 統合 / ミクロのスパイク Jaccard | 0.9610 / 0.9590 - ヌル対照（重みシャッフル、実トポロジー）：0.6546、偶然より +0.31 上 |
| | van Rossum 類似度（tau = 2） | 0.9941 |
| | 読み出し Pearson / 余弦 / SQNR | 0.9226 / 0.9565 / 29.6 dB |
| | 総発火数 量子化 vs 浮動 | 30,411 vs 30,450（0.13%）；発火数 r 0.9975、Spearman 0.9767 |
| カーネル単体、Brette 型閉形式検査 | 12,800 の 4 ティックにわたる減衰 | 11,806 = LUT を通した厳密な 200 x 0.98^4 x 64；30 ティックにわたるビット同一の `stateRoot` |

**範囲を率直に。** 検査 1 は本配備で証明済みである。検査 2-3 は、この生物の同胞配備（同一の参照脳とカーネル系譜）で測定された；それらは、刻印バックボーンが合意された壁を超えて完全 13.6M 辺結合組の力学を再現することを確立する - 他のグループのシミュレーションとの行動的等価ではない。

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

## フィールド研究

生物の放出履歴それ自体が一つの研究コーパスである。`research/` の下の各研究は完全で自己検証するパッケージである - 報告、図、機械可読データ、そしてすべての数字をコンセンサスから再導出する道具。研究は英語・中国語（`.zh.md`）・日本語（`.ja.md`）の三版で発表される；データ・図・検証成果物は全版で共通である。

| 研究 | 窓 | 主題 |
|---|---|---|
| `research/2026-09-22-brainstate-census/` | ティック 1-74（ブロック 21,181,651-22,041,291） | 最初の五日間のコンセンサス実行神経生理学：`BrainState` の網羅的センサス、バイト厳密な双生体リプレイ、感覚上皮のダイナミクス |

```bash
python3 tools/verify_census.py        # 鎖を再走査し、センサスと比較する
python3 tools/verify_twin.py --fired $(cat research/2026-09-22-brainstate-census/data/poke_inputs.txt)
```

---

## 本リポジトリ

| パス | それは何か |
|---|---|
| `src/ImmortalFruitFlies.sol` | 凍結されたカーネル：電位、減衰、レーン、`think`（改名するな - パスは配備バイトコードのメタデータにハッシュされ検証される） |
| `src/ImmortalFruitFliesTape.sol` | 一本のテープコントラクト：ランタイムコードとしての結合組の切片 |
| `src/Obrain.sol` | 代謝：60 チャネル、バーンティア、`feed()` |
| `tapes/` | 全 85 本の結合組ペイロード、配備どおりに |
| `annotations/` | 細胞構築表：細胞あたり 5 バイト（超クラス、細胞クラス、細胞型、region、side、flow）、カーネル索引空間における BANC v888 メタデータ |
| `tools/verify_tapes.py` | バイト同一性の証明：オンチェーンのテープコード vs `tapes/`（標準ライブラリのみ） |
| `tools/tapes.py`、`tools/vbrain.py` | カーネルのベクトル化された、鎖厳密な双生体（numpy） |
| `tools/verify_twin.py` | 決定論的リプレイ：求入語を与えれば、すべてのスパイク列と `stateRoot()` を再生する |
| `tools/verify_census.py` | Arc から `BrainState`/`Feed` ログを再走査し、同梱センサスと比較する（標準ライブラリのみ） |
| `research/` | フィールド研究：報告、図、機械可読データ、検証ログ |
| `LICENSE`、`LICENSE-DATA` | 二つのライセンス：コードは AGPL-3.0-only、派生データ成果物は CC BY-NC-SA 4.0 |
| `foundry.toml` | ビルド設定（solc 0.8.28、via_ir、cancun） |

```bash
forge build
```

作業リポジトリ（インデクサ、3D ライブビュー、配備）は非公開；本リポジトリは生物だけを保つ。

---

## ライセンスと引用

本リポジトリのライセンスは厳格に、著者の権利を優先する。二つのライセンス、いずれも執行可能である：

- **コード**（`src/`、`tools/`、`foundry.toml`、SPDX タグと一致）-
  **GNU AGPL-3.0-only**、[LICENSE](LICENSE) を見よ。最も強い標準的なコピーレフト：このコードの上に築き、それを配備し、それをサービスとして提供する者は - オンチェーンであれオフチェーンであれ - 対応するソースを同一の条件の下で公開しなければならない。生物の機構を閉じた仕事へ呑み込むことは許されない。
- **派生データ成果物**（`tapes/`、`annotations/`、および `research/` の下のデータと図）-
  **CC BY-NC-SA 4.0**、[LICENSE-DATA](LICENSE-DATA) を見よ。帰属は必須、商業利用は著者の別個の許可を要し、翻案は同一ライセンスを前へ携える。必須の帰属：Bates, A.S. et al.
  *Distributed control circuits across a brain-and-cord connectome.*
  Nature 656, 957-970 (2026), doi:10.1038/s41586-026-10735-w、および本リポジトリのすべての成果物が由来する BANC v888 リリース。

本変更より前に発表された本リポジトリの版は MIT（コード）と CC-BY-4.0（データ）を帯びており、それらの条件の下で引き続き入手可能である；本条件はこの版および以後のすべての版を縛る。Arc 上の配備済みコントラクトは本変更に先行し、変更なく実行される。上流の BANC データは BANC プロジェクトのものであり、その自身の条件の下にある；本リポジトリは上流の何ものも再ライセンスしない。
