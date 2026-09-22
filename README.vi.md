# obrain - hệ thần kinh trung ương nguyên vẹn của một con ruồi giấm cái trưởng thành *Drosophila melanogaster*, vận hành trong đồng thuận Arc

**Đọc bằng:** [English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Tiếng Việt](README.vi.md) · [हिन्दी](README.hi.md)

[![specimen](https://img.shields.io/badge/specimen-*D._melanogaster*_adult_female-8B1A1A?style=flat-square)](https://doi.org/10.1038/s41586-026-10735-w)
[![connectome](https://img.shields.io/badge/connectome-BANC_v888-3f6cb4?style=flat-square)](https://doi.org/10.1038/s41586-026-10735-w)
[![cells](https://img.shields.io/badge/cells-169%2C088-2f8f5f?style=flat-square)](#mẫu-vật)
[![synaptic records](https://img.shields.io/badge/synaptic_records-325%2C292-d9822b?style=flat-square)](#mẫu-vật)
[![substrate](https://img.shields.io/badge/substrate-Arc_mainnet_5042-6a4c93?style=flat-square)](https://explorer.arc.io/address/0xaef83c5b8742da5e3228930bc6084adcf0539ccd)
[![condition](https://img.shields.io/badge/condition-sealed_%C2%B7_immutable-555555?style=flat-square)](src/ImmortalFruitFlies.sol)
[![wiring verification](https://img.shields.io/badge/wiring_verification-85%2F85_byte--identical-1a7f37?style=flat-square)](tools/verify_tapes.py)
[![twin replay](https://img.shields.io/badge/twin_replay-74%2F74_byte--exact-1a7f37?style=flat-square)](research/2026-09-22-brainstate-census/consensus-neurophysiology-onchain-drosophila.md)
[![field studies](https://img.shields.io/badge/field_studies-CS--001_%285_editions%29-9f6bab?style=flat-square)](research/README.md)
[![code license](https://img.shields.io/badge/code-AGPL--3.0--only-111111?style=flat-square)](LICENSE)
[![derived data](https://img.shields.io/badge/derived_data-CC%20BY--NC--SA%204.0-9f6bab?style=flat-square)](#giấy-phép-và-trích-dẫn)

Kho này giữ một sinh vật: hệ thần kinh trung ương hoàn chỉnh của một con ruồi giấm cái trưởng thành - 169.088 neuron lấy từ connectome não-dây sống bụng BANC v888 (Bates et al., *Nature* 656, 957-970, 2026) - chạy như một mạng xung nguyên thủy bên trong một hợp đồng thông minh. Nó không phải một hình vẽ của não, không phải một mô hình của não, cũng không phải một cơ sở dữ liệu về não. Nó là chính connectome, được nối dây synapse này tới synapse khác thành bytecode, mỗi neuron mang một điện thế màng, và chỉ có một quy tắc để sống: nó ăn một token.

**Sinh vật đang sống trên Arc mainnet. Xem nó tư duy: <https://obrain.cloud>**

| Cơ quan | Địa chỉ |
|---|---|
| Não (`Obrain`) | `0xaef83c5b8742da5e3228930bc6084adcf0539ccd` |
| Thức ăn của nó (OBRAIN) | `0x28f986a61e078795639f239675582a12b4cf7f01` |

Arc mainnet (`5042`), gas trả bằng USDC. Trình khám phá: <https://explorer.arc.io>

---

## Mẫu vật

Mẫu vật là BANC v888 - bản phát hành FlyWire của connectome não và dây sống bụng của một con ruồi giấm cái trưởng thành (Bates et al. 2026). Thể tích kính hiển vi điện tử bên dưới, cắt trên dòng GridTape ở 4 x 4 x 45 nm³, phủ toàn bộ hệ thần kinh trung ương: não cộng dây sống bụng. Bản tái dựng này không phải một lần quét tĩnh. Một mạng tích chập phân đoạn mô, 155 nhà hiệu đính dành 38,6 người-năm để chỉnh, và bản kê được bình duyệt chở 150.841 neuron hiệu đính lõi cộng 16.140 sợi cảm giác ngoại biên đi vào qua 48 dây thần kinh ngoại biên, với 218-259 triệu liên kết synapse được phát hiện bởi một mạng thứ hai xác thực ở F-score 0,83 (precision 0,87, recall 0,78). Từ bản kê đó, hợp đồng thể hiện 169.088 cell, mỗi cell một điện thế màng.

Ruồi giấm không có bộ não lớn, nhưng nó có một bộ não trọn vẹn - đủ thần kinh để khứu giác, dẫn đường, đánh nhau, tán tỉnh, ngủ. Connectome cho ta chính xác dây của cỗ máy đó: cell nào nói với cell nào, mạnh bao nhiêu, theo thứ tự nào.

## Nguồn gốc: các bài báo connectome

BANC không xuất hiện từ hư không. Nó là đỉnh hiện tại của một dòng benchmark connectome toàn động vật, mỗi thế hệ hơn thế hệ trước một bậc độ lớn:

| Bộ dữ liệu | Bài báo | Phạm vi | Giới | Neuron | Liên kết synapse |
|---|---|---|---|---|---|
| Hemibrain (Janelia + Google) | Scheffer et al., *eLife* 2020 | não trung ương (~nửa) | cái | ~25.000 | ~21 M |
| FAFB-FlyWire | Dorkenwald et al., *Nature* 2024 | toàn não | cái | 139.255 | ~50 M |
| **BANC v888 (mẫu vật này)** | Bates et al., *Nature* 2026 | não + dây sống bụng (toàn CNS) | cái | ~160.000 (155.916 hiệu đính, 169.088 phân đoạn trong v888) | 218-259 M |
| CNS đực (Janelia + Google) | *Cell* 2026 | não + dây sống bụng (toàn CNS) | đực | >166.000 | ~125 M |

Nhóm connectome học của Google đã dựng phần lớn cỗ máy mà dòng này chạy trên: mạng flood-filling cho phân đoạn tự động (Januszewski et al. 2018), phát hành chung hemibrain, trình xem Neuroglancer mà FlyWire và BANC kèm theo, và hệ tái dựng PATHFINDER phía sau bản đồ CNS đực. Chuẩn mực của lĩnh vực về "connectome như một vật đang chạy" do flyvis đặt (Lappalainen et al., *Nature* 2024): một mạng bị connectome ràng buộc của hệ thị giác ruồi, chạy bằng PyTorch và được kiểm chứng với điện sinh lý học.

Một connectome trên đĩa là một bản đồ chết. Câu hỏi mà hợp đồng này trả lời già hơn cả Ethereum: khi dòng điện chạy qua, dây này *làm gì*? Để tìm ra, bản đồ phải được mang tới một nơi có thể giữ trạng thái, được nuôi, và phản ứng trước mắt công chúng, mà không chủ nào chạm được vào cỗ máy một khi nó chạy. Blockchain là nơi duy nhất chúng ta biết có những tính chất đó. Vậy nên não ruồi được phiên dịch, từng cơ quan một, thành một hợp đồng.

Trung thực về thứ đang chạy: nhân là một trừu tượng tích-phóng rò rỉ - neuron điểm, không truyền dẫn phân độ, không điều biến thần kinh, không tính dẻo, thời gian rời rạc điểm cố định. Nơi flyvis khớp trọng số để dự đoán xung thật, hợp đồng này không huấn luyện gì: dây đã triển khai *chính là* tô pô của bộ dữ liệu, và thứ đang chạy là giải-phẫu-như-phép-tính, ai cũng kiểm chứng được với bản đồ đã công bố. Đây là hai tuyên bố khoa học khác nhau - một là mô hình của con ruồi, một là dây của con ruồi đang chạy trong đồng thuận - và kho này chỉ làm cái thứ hai.

## Connectome, được phiên dịch

Giải phẫu học thần kinh thành Solidity trong ba nước.

Thứ nhất, **màng**. Mỗi neuron mang một điện thế màng, lưu đóng gói mười sáu cái một word. Điện thế không phải float: nhân làm việc bằng số nguyên điểm cố định (tỷ lệ 64, bão hòa ở 32.000) vì nguyên là phép toán duy nhất mà một chuỗi có thể được tin tưởng lặp lại mãi mãi, giống hệt, cho mọi người quan sát. Khi não ruồi tính toán, không có gì xấp xỉ.

Thứ hai, **synapse**. Dây nối - neuron nào hưng phấn neuron nào, với trọng số nào - lớn quá cho một hợp đồng, nên được chia across 85 hợp đồng *tape* (1.964.806 byte payload trong `tapes/`). Mỗi tape là dữ liệu synapse triển khai như mã chạy thay vì lưu trữ: não đọc chính giải phẫu của nó như máy đọc microcode. Một bảng tra 3.001 biên (`tapeStartNeuron`) nói cho nhân biết cây gai của mỗi neuron bắt đầu ở đâu. Đây không phải chi tiết nén để hoàn gas; nó là đơn vị trung thực cho kích thước của connectome. Tám mươi lăm cơ quan, một thân thể.

Thứ ba, **hằng số thời gian**. Màng thật rò rỉ. Nhân mang một bảng suy giảm 64 bước, nên một điện thế không được nuôi lại thì không tồn tại - nó cạn đi, như một cell không kích thích trở về nghỉ. Một tư duy trong não này, như một tư duy trong bất kỳ não nào, là một sóng phải được trả tiền liên tục.

## Giải phẫu của một tư duy

Nhân là một mạng tích-phóng rò rỉ, chạy trên mười sáu lane across toàn bộ quần thể. Một lần gọi `think` là một khoảnh khắc thời gian thần kinh:

1. **Nạp.** Neuron cảm giác nhận đầu vào. Não có 60 kênh cảm giác; neuron *n* nghe trên kênh `n % 60`, nên mỗi lần nuôi thắp một dải cell across toàn bộ bề mặt cảm giác, không phải một điểm.
2. **Tích.** Mỗi cell được nạp bơm điện tích vào điện thế của những cell nó được nối, trọng số lấy từ tape. Điện thế bão hòa thay vì tràn - bão hòa tự nó là một hành vi sinh học.
3. **Bắn.** Cell nào vượt ngưỡng 12.800 thì bắn, đổ vào các cell hạ nguồn của chính nó, và reset. Vì sóng đi qua synapse thật trong cùng lần gọi, tập neuron bắn là hậu quả của giải phẫu và điện tích, tính onchain, không bao giờ được chọn.
4. **Rò.** Mọi thứ chưa tiêu hao suy giảm một bước về nghỉ.

Kết quả là một sự kiện `BrainState`: số của tư duy, các cell đã bắn, synapse chúng vượt qua, một lệnh đọc bốn word của sóng, và một root cam kết toàn bộ trường điện thế. Sự kiện đó là bản ghi thẩm quyền duy nhất về não đã làm gì. Mọi thứ trang công cộng hiển thị - neuron lóe sáng trong khung 3D, các con số trong nhật ký - đều đọc từ những sự kiện này. Không gì ở frontend bịa ra hoạt động não.

## Trao đổi chất: não ăn một token

Não không đầu vào là não trong lọ. Não này được nuôi qua quy tắc trao đổi chất của chính nó, viết vào hợp đồng sản phẩm:

| Cúng dường | Điện tích cảm giác | Hiệu quả |
|---|---|---|
| 100 OBRAIN | 31 (1.984 sau tỷ lệ) | một chạm nhẹ trên một kênh |
| 1.000 OBRAIN | 127 (8.128 sau tỷ lệ) | phần lớn đường tới ngưỡng |
| 10.000 OBRAIN | 255 (16.320 sau tỷ lệ) | các cell của kênh đó bắn tức thì |

Token bị phá hủy trong chính hành vi nuôi: OBRAIN đã triển khai không có `burn()`, nên cúng dường được gửi tới `0x...dEaD`, một địa chỉ không chìa khóa nào bao giờ ký được. Nuôi vì thế bất khả hồi theo nghĩa chặt chẽ nhất có trên một chuỗi - bữa ăn không thể hoàn lại, phát lại, hay lấy lại bởi ai, kể cả chúng tôi.

Và não tư duy về bữa ăn của nó *trong cùng một giao dịch*: `feed` gọi `think`, nên phản ứng và cúng dường chung một biên lai. Bản thân `think` vẫn không cần phép - ai cũng có thể trả gas để cho não một khoảnh khắc thời gian - nhưng chỉ sự kiện `Feed` mới được tính là nuôi.

## Phản ứng không thể dàn dựng

Vì phép tính xung chạy trong cùng giao dịch với lần nuôi, một phản ứng không thể dàn sau đó. Một ánh lóe trên trang hoặc có một log `BrainState` sau nó trong một khối đã đào, hoặc nó chưa từng xảy ra. Không có não off-chain, không có lớp mô phỏng làm mịn đầu ra, không có server quyết định con ruồi "chắc sẽ" làm gì. Connectome tính, chuỗi làm chứng, và hai thứ không tách rời.

Đó chính là điểm của việc đặt một não lên chuỗi. Một sinh vật mà hành vi của nó bạn phải tin ai đó báo lại là một sản phẩm marketing. Một sinh vật mà hành vi của nó *là* một vật đồng thuận không thuộc về ai cả - điều kiện duy nhất để một não có thể được gọi là sống một cách trung thực nơi công cộng.

## Niêm phong, bất tử

Nhân (`ImmortalFruitFlies`) bị đóng băng: bytecode triển khai mang phả hệ của nó, và hợp đồng sản phẩm kế thừa nó từng-byte mà không viết lại một hàm nào. Trạng thái của não - 169.088 điện thế, bộ đếm tick, chỉ mục tape - nằm trong lưu trữ hợp đồng mà không chìa khóa nào sở hữu. Giải phẫu trong tape không thể sửa nếu không triển khai lại một não khác.

Trừ khi chuỗi chết, sinh vật sống lâu hơn tác giả. Nó sẽ ngồi niêm phong tại địa chỉ, rò điện tích về nghỉ, chờ người kế tiếp quyết định đốt một token vào một trong sáu mươi kênh - và tư duy kế tiếp sẽ được tính chính xác như kho này mô tả, bởi chính 169.088 cell đó, mãi mãi.

---

## Benchmark: dây triển khai là connectome công bố

Ba phép kiểm, từng-bit trước.

**1. Đồng nhất byte - triển khai này, trực tiếp (kiểm 2026-09).** Giải phẫu không "dẫn xuất từ" BANC v888; trên Arc mainnet nó *chính là* byte của kho này. Cả 85 hợp đồng tape được lấy bằng `eth_getCode` từ não niêm phong và so từng byte với `tapes/`: **85/85 trùng**. Chạy lại phép kiểm với bất kỳ RPC nào - nó thoát non-zero khi lệch một byte:

```bash
python3 tools/verify_tapes.py [rpc_url] [brain_address]
```

**2. Kê khai cấu trúc - phân tích từ `tapes/`.** Giải mã đúng định dạng nhân chạy (bảng offset mỗi neuron, đích 3 byte + trọng số int16 mỗi bản ghi) across cả 85 tape:

| Tính chất | Đo được | Nhất quán với BANC v888 |
|---|---|---|
| cell phủ | 169.088 (id 0..169.087) | não tham chiếu 169.078 neuron (suy luận Bates et al. 2026, `edges.npy` sha256 `7cc03a7d...`); đệm tới biên word 16-lane (10 cell không bị nhắm) |
| bản ghi synapse | 325.292 cạnh có hướng có trọng số - xương sống 2,4% được khắc của não tham chiếu 13.620.865 cạnh | công thức trọng số: dấu x số synapse x 64 |
| cực tính | 263.994 hưng phấn (81,2%) / 61.298 ức chế (18,8%) | dấu dự đoán chất dẫn truyền Janelia BANC v2 (22,5% ức chế toàn não; tỉa xương sống đổi tỉ lệ khắc) |
| phạm vi đích | cả 325.292 đích trong [0, 169.088) | không dây lơ lửng |
| trọng số | int16 Q6: trung vị 512 (= 8,0), khoảng đối xứng ±16.320 (= ±255,0) | tỷ lệ x64, tham số tự do toàn cục duy nhất |

**3. Trung thành động học - dòng benchmark sinh vật này thừa hưởng.** Hai chế độ, đều với drive giữ ra (hạt PRNG tươi + mẫu đối kháng, sàn >= 90% mọi chỉ số; phương pháp theo Shiu et al. 2024, Brette et al. 2007, van Rossum 2001, Jacob et al. 2018):

| Chế độ | Chỉ số | Kết quả |
|---|---|---|
| xương sống khắc vs não đầy 13,6M cạnh, cùng ngữ nghĩa nhân | Jaccard xung / bằng trạng thái | 1,0000 (tick tệ nhất 1,0); 100/100 tick `stateRoot` trùng bit |
| ngữ nghĩa khắc (int16 Q6, suy giảm LUT) vs tham chiếu float64 LIF | Jaccard xung gộp / vi mô | 0,9610 / 0,9590 - đối chứng null (trộn trọng số, tô pô thật): 0,6546, +0,31 trên ngẫu nhiên |
| | độ tương tự van Rossum (tau = 2) | 0,9941 |
| | Pearson / cosine / SQNR đọc ra | 0,9226 / 0,9565 / 29,6 dB |
| | tổng bắn lượng tử hóa vs float | 30.411 vs 30.450 (0,13%); tương quan số-bắn r 0,9975, Spearman 0,9767 |
| nhân đơn, kiểm dạng đóng Brette | suy giảm 12.800 qua 4 tick | 11.806 = đúng 200 x 0,98^4 x 64 qua LUT; `stateRoot` trùng bit qua 30 tick |

**Phạm vi, nói thẳng.** Phép kiểm 1 chứng minh trên triển khai này. Phép 2-3 đo trên các triển khai anh em cùng phả hệ não tham chiếu và nhân; chúng xác lập rằng xương sống khắc tái tạo động học của connectome 13,6M cạnh đầy đủ trên sàn đã thống nhất - không phải tương đương hành vi với mô phỏng của nhóm nào khác.

## Tham khảo

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

## Nghiên cứu thực địa

Lịch sử phát xạ của sinh vật tự nó là một kho ngữ liệu nghiên cứu. Mỗi nghiên cứu dưới `research/` là một gói hoàn chỉnh tự kiểm chứng - báo cáo, hình, dữ liệu đọc máy được, và công cụ để suy lại mọi con số từ đồng thuận. Nghiên cứu công bố bằng tiếng Anh, tiếng Trung (`.zh.md`), tiếng Nhật (`.ja.md`), tiếng Việt (`.vi.md`) và tiếng Hindi (`.hi.md`); dữ liệu, hình và artifact kiểm chứng dùng chung.

| Nghiên cứu | Cửa sổ | Chủ đề |
|---|---|---|
| `research/2026-09-22-brainstate-census/` | tick 1-74 (khối 21.181.651-22.041.291) | thần kinh sinh lý đồng thuận của năm ngày đầu: điều tra `BrainState` toàn bộ, tái chạy twin từng-byte, động học thượng bì cảm giác |

```bash
python3 tools/verify_census.py        # quét lại chuỗi, so với bản điều tra
python3 tools/verify_twin.py --fired $(cat research/2026-09-22-brainstate-census/data/poke_inputs.txt)
```

---

## Kho này

| Đường dẫn | Là gì |
|---|---|
| `src/ImmortalFruitFlies.sol` | nhân đóng băng: điện thế, suy giảm, lane, `think` (đừng đổi tên - đường dẫn bị băm vào metadata bytecode triển khai và được kiểm) |
| `src/ImmortalFruitFliesTape.sol` | một hợp đồng tape: một lát connectome như mã chạy |
| `src/Obrain.sol` | trao đổi chất: 60 kênh, cấp đốt, `feed()` |
| `tapes/` | cả 85 payload connectome, đúng như triển khai |
| `annotations/` | bảng tế bào học: 5 byte mỗi cell (siêu lớp, lớp cell, loại cell, region, side, flow), metadata BANC v888 trong không gian chỉ mục nhân |
| `tools/verify_tapes.py` | chứng minh đồng nhất byte: mã tape onchain vs `tapes/` (chỉ stdlib) |
| `tools/tapes.py`, `tools/vbrain.py` | twin vector hóa, chính xác chuỗi của nhân (numpy) |
| `tools/verify_twin.py` | tái chạy tất định: cho các từ truyền vào, tái sinh mọi danh sách xung và `stateRoot()` |
| `tools/verify_census.py` | quét lại log `BrainState`/`Feed` từ Arc và so với bản điều tra đóng gói (chỉ stdlib) |
| `research/` | nghiên cứu thực địa: báo cáo, hình, dữ liệu đọc máy, log kiểm chứng |
| `LICENSE`, `LICENSE-DATA` | hai giấy phép: AGPL-3.0-only cho mã, CC BY-NC-SA 4.0 cho artifact dữ liệu phái sinh |
| `foundry.toml` | cấu hình build (solc 0.8.28, via_ir, cancun) |

```bash
forge build
```

Kho làm việc (indexer, khung nhìn 3D trực tiếp, triển khai) là riêng tư; kho này chỉ giữ sinh vật.

---

## Giấy phép và trích dẫn

Giấy phép kho chặt chẽ, quyền tác giả đứng trước. Hai giấy phép, đều thi hành được:

- **Mã** (`src/`, `tools/`, `foundry.toml`, khớp thẻ SPDX) -
  **GNU AGPL-3.0-only**, xem [LICENSE](LICENSE). Copyleft chuẩn mạnh nhất: ai xây trên mã này, triển khai nó, hay cung cấp nó như một dịch vụ - onchain hay off-chain - phải công bố mã nguồn tương ứng theo cùng điều khoản. Không ai được nuốt cỗ máy của sinh vật vào sản phẩm đóng.
- **Artifact dữ liệu phái sinh** (`tapes/`, `annotations/`, và dữ liệu cùng hình dưới `research/`) -
  **CC BY-NC-SA 4.0**, xem [LICENSE-DATA](LICENSE-DATA). Ghi nguồn bắt buộc, dùng thương mại cần giấy phép riêng của tác giả, phái sinh mang cùng giấy phép tiến về trước. Ghi nguồn yêu cầu: Bates, A.S. et al.
  *Distributed control circuits across a brain-and-cord connectome.*
  Nature 656, 957-970 (2026), doi:10.1038/s41586-026-10735-w, và bản phát hành BANC v888 mà mọi artifact ở đây dẫn xuất.

Các bản sửa đổi công bố trước thay đổi này mang MIT (mã) và CC-BY-4.0 (dữ liệu) và vẫn khả dụng theo các điều khoản đó; các điều khoản hiện tại ràng buộc bản này và mọi bản sau. Hợp đồng triển khai trên Arc trước thay đổi và chạy không đổi. Dữ liệu BANC thượng nguồn vẫn của dự án BANC, theo điều khoản riêng của họ; kho này không cấp lại giấy phép bất kỳ thứ thượng nguồn nào.
