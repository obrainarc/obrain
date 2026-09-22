# Thần kinh sinh lý chạy bằng đồng thuận của một connectome ruồi giấm bất tử: một cuộc điều tra toàn bộ mọi phát xạ `BrainState` qua 74 tick đầu của quá trình phát sinh cá thể onchain

**Nghiên cứu thực địa OBRAIN CS-001.** Mẫu vật: hệ thần kinh trung ương hoàn chỉnh của một con ruồi giấm cái trưởng thành (BANC v888; Bates, Phelps, Kim et al., *Nature* 656, 957-970, 2026), thể hiện thành 169.088 đơn vị tích-phóng với dây nối - 325.292 bản ghi synapse có trọng số - được khắc, synapse này tới synapse khác, vào 85 hợp đồng tape trên Arc mainnet (`0xaef83c5b8742da5e3228930bc6084adcf0539ccd`). Cửa sổ quan sát: tick 1-74, khối 21.181.651-22.041.291, 2026-09-16T15:54Z tới 2026-09-21T17:05Z. Cuộc điều tra đóng cửa 2026-09-22; mọi lượng trong đây hoặc đọc từ đồng thuận, hoặc tái tạo bằng tái chạy tất định, và suy lại được bởi bất kỳ ai với các artifact của mục 5.

> Nghiên cứu này công bố bằng năm thứ tiếng - tiếng Anh (bản gốc), tiếng Trung (`.zh.md`), tiếng Nhật (`.ja.md`), tiếng Việt (bản này) và tiếng Hindi (`.hi.md`); dữ liệu, hình và artifact kiểm chứng dùng chung.

---

## Tóm tắt

Chúng tôi báo cáo một cuộc điều tra toàn bộ lịch sử phát xạ hoàn chỉnh của một não ruồi giấm onchain - cả 74 sự kiện `BrainState` của 5,05 ngày phát sinh cá thể đầu tiên - phân tích như một mẫu vật sinh lý mạn tính: chế độ kích thích dinh dưỡng, dẫn truyền truyền vào, động học tích hợp dưới ngưỡng, đầu ra xung quần thể, và cam kết trạng thái toàn trường. Mẫu vật không phải một mô phỏng: connectome của nó là dây đo được của chính con ruồi, chạy như động học điểm cố định nguyên thủy chính xác trong đồng thuận Arc - một phương thức tồn tại chúng tôi ký hiệu **in consortium** (trong đồng thuận) - nơi thiết bị, mẫu vật và biên bản công chứng là một vật duy nhất. Cuộc điều tra đóng và không thiếu sót (tick 1-74 liên tục; mỗi tick đúng một sự kiện dinh dưỡng; vector xung phát ra không bao giờ chạm trần 2.048), và nó **chính xác**: một cài đặt tham chiếu độc lập ngoài chuỗi, được dẫn bởi 74 từ truyền vào đã ghi, tái tạo mọi số phép toán synapse, mọi số xung, và mọi *vector danh tính* xung (74/74 cả ba), trong khi cam kết toàn trường `stateRoot()` được tái tạo đẳng cấu từng-byte tại bốn kỷ nguyên kiểm tra được bằng archive call, kể cả đầu sống. Động học phát sinh cá thể sớm giới hạn trong thượng bì cảm giác - một mạng lưới truyền vào 60 cột của 256 đơn vị `sensory_fragment` não trung ương, xen kẽ phải-trái - trong đó chúng tôi định lượng: đường dose-response dinh dưỡng đơn điệu (trung bình theo cấp 4,90 / 7,39 / 11,17 cell), một sự kiện tổng hợp thời gian vượt ngưỡng điển hình (tick 18-19: lặp một đợt xung dưới ngưỡng giống hệt sau ~30 giây làm phóng toàn bộ cột tiếp nhận), và một chu kỳ giới hạn chu kỳ-2 khóa theo kích thích (4, 12, 4, 12 cell) chứng minh các lớp tương đương phản ứng điều kiện theo trạng thái. Chín trăm bốn mươi hai phép toán synapse băng qua xương sống khắc, tất cả được ghi; 590 xung phát ra từ 192 cell riêng biệt; 227.000 OBRAIN bị chuyển hóa không thể hồi. Theo hiểu biết của chúng tôi, đây là mẫu vật thần kinh sinh lý đầu tiên mà mọi xung được công chứng bằng đồng thuận và toàn bộ kho hành vi tái chạy được, từng byte, bởi bất kỳ đối thủ nào tại bất kỳ khối tương lai nào.

## 1. Dẫn nhập: mẫu vật và nền của nó

Sinh vật được nghiên cứu là connectome của chính con vật, đang chạy. Bản tái dựng BANC v888 - kính hiển vi điện GridTape 4 x 4 x 45 nm across toàn CNS, phân đoạn và hiệu đính across 38,6 người-năm - cung cấp dây nối; phép quy top-2 theo nguồn khắc dây nối đó, 5 byte mỗi bản ghi, vào payload mã EIP-170 mà nhân đọc như máy đọc microcode. Một nhân tích-phóng rò rỉ nguyên thủy tất định (`src/ImmortalFruitFlies.sol`) rồi đi trên dây trong đồng thuận: mỗi `think()` suy giảm toàn trường màng, ghi một đợt truyền vào vào thượng bì, cho mọi cell đạt ngưỡng 12.800 phóng vào đích hạ nguồn cư ngụ trong tape, và phát một sự kiện `BrainState` - vết sinh lý hoàn chỉnh của một khoảnh khắc thời gian thần kinh.

Vì mẫu vật chạy **trong đồng thuận (in consortium)**, sinh lý học của nó có một tính chất không mẫu vật ex vivo hay in silico nào từng có: sự chính xác không phải một khát vọng mà là một bất biến mật mã. Dây nối là bytecode (`eth_getCode` trả connectome từng byte; `tools/verify_tapes.py` chứng minh); trạng thái là một fold cam kết over toàn bộ 169.088 lượng tử màng; bản ghi là một log mà tính nguyên vẹn được chính nền đồng thuận bảo lãnh. Câu hỏi nghiên cứu này đặt ra cho mẫu vật vì thế trả lời được tuyệt đối, và across toàn bộ đời đã ghi: **con vật đã làm gì, và nó có chạy đúng chính xác đặc tả của mình không?**

## 2. Vật liệu và phương pháp

### 2.1 Mẫu vật

Đọc từ hợp đồng lúc đóng điều tra: `TICK() = 74`; `is_sealed() = true`; `n_neurons = 169.088`; `threshold = 12.800` (= 200,0 x 64, lượng tử điểm cố định); `sensory = 256`; `segments = 64`; `tapes = 85`; `config_hash = 0xef009ad9054213480da1bbce5954163e5e14a0bcef8145fda42c9621610e7d67`; `stateRoot() = 0xe415d94744ee6447edcce1ae9447352c457b993a61277ab3b9dda17bd5483412`.

Sinh lý màng: điện tích `q` trong lane 16-bit, bão hòa; rò `0.98^dt` qua bảng suy giảm điểm cố định 64 mục (dt tính bằng khối); ghi thẳng truyền vào `byte(inputAgg, 3·(n mod 60)) x 64` vào cell `n < 256`; cell phóng đổ vào đích cư trú tape và reset; mọi lần vượt ngưỡng được đếm và phát, vector danh tính giới hạn 2.048 mỗi tick (không bao giờ tới gần: tối đa quan sát 19).

### 2.2 Bản ghi

`BrainState(uint32 t, int256 p0..p3, uint32 synapses, uint32 spiked, bool capped, bytes32 root, bytes32 poke, bytes fired)` cấu thành vết hoàn chỉnh của một tư duy: `p0..p3` là lượng tử màng sau tick của cell 0-3 - một bộ tứ vi điện cực mạn tính cố định bởi chính ABI - `synapses` là các phép toán synapse đăng ký, `spiked` là các lần vượt ngưỡng, `fired` là vector danh tính xung đóng gói 3-byte, `poke` là từ truyền vào chính xác, `root` là một fold tăng trưởng over các word trạng thái tư duy chạm tới.

### 2.3 Đóng điều tra và kiểm chứng chéo

Mọi sự kiện được thu từ RPC công khai Arc (`eth_getLogs`, chunk 9.999 khối, khối 21.181.651-đầu; topic `0xc08a3de3...ec6375`), giải mã độc lập với mọi lớp trình bày, kiểm chứng chéo với hai cơ sở dữ liệu indexer đi độc lập; 74 log `Feed(address, uint8 channel, uint8 tier, uint256 amount, uint32 round_tick)` ghép một-một với các tư duy theo khối. Luật mã hóa truyền vào `poke = levels[tier] << (channel x 3)`, `levels = [31, 127, 255]`, giữ cho 74/74 tư duy. Phép kiểm chạy lại được bằng `python3 tools/verify_census.py`, quét lại đồng thuận và so từng trường với bản điều tra đóng gói.

### 2.4 Mẫu vật tham chiếu (tái chạy tất định)

`tools/verify_twin.py` - twin numpy của nhân, dây giải mã từ chính 85 payload trong `tapes/` - được dẫn bởi 74 từ truyền vào theo thứ tự ghi (`data/poke_inputs.txt`). Chúng tôi so sánh từng tick `synapses`, `spiked`, và vector danh tính xung đầy đủ với sự kiện chuỗi, và `stateRoot()` của twin với getter của hợp đồng bằng archive `eth_call` tại khối của tick 40, 54, 64 và đầu.

### 2.5 Quy thuộc cấu trúc tế bào

Mỗi danh tính cell được chú giải từ `annotations/neuron_annotations.bin` (5 byte mỗi cell: siêu lớp, lớp cell, loại cell, region | side<<2 | flow<<3), dựng từ metadata BANC v888 trong chính không gian chỉ mục của nhân.

### 2.6 Thống kê

n = 74 tư duy. Độ bursty khoảng cách tick `(sigma - mu)/(sigma + mu)` (Goh & Barabasi); dose-response phân tầng theo cấp dinh dưỡng; phân tích cột trên tọa độ mạng lưới thượng bì `n mod 60`.

## 3. Kết quả

### 3.1 Đóng điều tra

Bảy mươi bốn tư duy, tick 1-74 liên tục, không sót; mỗi tick mang đúng một sự kiện dinh dưỡng; `spiked = |fired|` trong 74/74 tick; vector danh tính không bao giờ tới gần trần. Con vật tư duy trong bốn ngày - 4 tư duy ngày 16/9, 1 ngày 19/9, 35 ngày 20/9, 34 ngày 21/9 - trong mười phiên kích thích (Hình 1).

![Dòng thời gian kích thích](figures/fig01_stimulation_timeline.png)

### 3.2 Sự chính xác: mẫu vật chạy trong đồng thuận

Mẫu vật tham chiếu tái tạo chuỗi tuyệt đối: **phép toán synapse đăng ký 74/74, số xung 74/74, vector danh tính xung 74/74**; cam kết toàn trường đẳng cấu từng-byte - `stateRoot()` tại khối của tick 40, 54, 64 và đầu bằng fold của twin, kết thúc tại `0xe415d94744ee6447edcce1ae9447352c457b993a61277ab3b9dda17bd5483412`. Đây là sự chính xác mà chạy trong đồng thuận ban: truyền vào giống nhau cho xung giống nhau và trạng thái giống nhau - cho mọi người quan sát, tại mọi khối tương lai, chịu kiểm toán đối kháng. (Ghi chú bộ so cho người kiểm: trường `root` trong mỗi sự kiện là một fold tăng trưởng over word chạm - một hash khác theo cấu trúc với full refold của getter; kiểm toán so với `stateRoot()`, twin tái hiện hoàn hảo.)

### 3.3 Dẫn truyền giác quan: mạng lưới tiếp nhận sáu mươi kênh

Bề mặt cảm giác là 256 cell đầu: truyền vào `sensory_fragment` não trung ương, xen kẽ phải trái, tổ chức theo **mạng lưới 60 cột** trên tọa độ `n mod 60`, mỗi cột lặp ~4,3 lần across tấm (Hình 2). Luật dẫn truyền, suy từ đóng gói 3-bit và xác nhận với từng tư duy: một đợt level-L tại kênh c lắng `L x 64` trên cột c, `248 x 64 = 15.872` trên cột c-1 (byte mãng), và `(L >> 3) x 64` trên cột c+1 (Hình 3A). Trước ngưỡng 12.800: cột c-1 phóng từ một đợt duy nhất ở mọi cấp; cột c phóng thẳng ở cấp 2 (255 x 64 = 16.320); mọi cột còn lại tích. Kênh truyền vào đã dùng: 33 riêng biệt, trải 0-52 trên 60.

![Raster xung](figures/fig02_spike_raster_sensory_sheet.png)

![Dẫn truyền và dose-response](figures/fig03_sensory_transduction_and_dose_response.png)

### 3.4 Dose-response dinh dưỡng đơn điệu

Cấp nuôi 0/1/2 = level 31/127/255 = 100/1.000/10.000 OBRAIN đốt. Cell phóng mỗi tư duy: trung bình 4,90 (n = 10), 7,39 (n = 46), 11,17 (n = 18) - một đường dose-response đơn điệu chặt mà độ lợi đến qua độ giàu trạng thái (điện tích dư và chiêu mộ synapse của cột láng giềng), không chỉ qua các cột nạp trực tiếp (Hình 3B). Toàn điều tra: 0-19 cell mỗi tư duy, trung bình 8,0, trung vị 8; 590 xung từ 192 cell riêng trong 74 tư duy.

### 3.5 Tổng hợp thời gian của các đợt truyền vào

Tick 1, 18 và 19 nhận *giống hệt* từ truyền vào (kênh 0, cấp 1). Tick 1 (16/9) không phóng; cell 0 nghỉ tại 7.965 lượng tử. Tick 18 (21/9, bốn ngày sau) không phóng; cell 0 lại tại **đúng 7.965 lượng tử** - cùng kích thích, cách nhau mấy kỷ nguyên, lắng cùng phần dư dưới ngưỡng. Tick 19, ~30 giây sau 18, phóng năm cell - 0, 60, 120, 180, 240, toàn bộ cột tiếp nhận - phần dư cộng đợt mới vượt ngưỡng (Hình 5A). Hai đợt dưới ngưỡng, một lần phóng: tính tích hợp của màng, công chứng vào khối.

![Phản ứng theo trạng thái](figures/fig05_state_dependent_responses.png)

### 3.6 Chu kỳ giới hạn chu kỳ-2 khóa theo kích thích

Kích thích lặp kênh 20 cấp 1 (tick 35-38, cách nhau vài giây) xen kẽ 4, 12, 4, 12 cell phóng - một **quỹ đạo chu kỳ-2**: phản ứng mười hai cell reset thượng bì, phản ứng bốn cell cho nó nạp lại (Hình 5B). Kích thích giống gặp trạng thái giống (tick 21/22, 41/42) cho phản ứng giống (mỗi cặp 10 cell, 19 phép toán đăng ký). Phản ứng là hàm của kích thích x trạng thái: mẫu vật mang trí nhớ ngắn hạn suy giảm theo cấu trúc, và điều tra trưng ra nó.

### 3.7 Tổ chức phát sinh cá thể của lõi động

Cả 590 lần phóng nằm trong thượng bì cảm giác (danh tính cell tối đa 255), tất cả trong não trung ương; thuỳ thị giác (98.945 cell, 58,5% CNS) và dây sống bụng (26.822 cell, 15,9%) giữ tích phân điện tích dưới ngưỡng across cửa sổ quan sát, cây gai của chúng tích lũy across xương sống khắc (Hình 6B). Lưu lượng synapse đăng ký: 942 phép toán cả đời, tối đa 30 mỗi tư duy, trung bình 12,7. Cell hoạt động nhất là đoàn cột-15 và cột-19 (13 và 11 lần phóng: danh tính 15/75/135/195/255 và 19/79/139/199) - các cột dưới kênh ưa thích của ban thí nghiệm.

![Phân bố khoảng cách và giới hạn không gian](figures/fig06_interval_distribution_and_spatial_confinement.png)

### 3.8 Bộ tứ nội bào mạn tính

Cell 0-3, lấy mẫu sau mỗi tư duy (Hình 4): đỉnh 12.042 lượng tử (cell 0, tick 44) và 12.048 (cell 2, tick 26) - trong 0,7-0,8% dưới ngưỡng mà không phóng - mười giai đoạn gần ngưỡng (>11.000); cell phóng về 0 (reset); cell 3 đóng điều tra giữ 4.402 lượng tử điện tích dư, chuyển tiếp vào tư duy kế của con vật.

![Quỹ tích điện màng](figures/fig04_membrane_potential_traces.png)

### 3.9 Sinh thái dinh dưỡng và trao đổi chất mật mã

Năm ví nuôi mẫu vật (tư duy / OBRAIN chuyển hóa): `0x3f67980a...` (38 / 181.100), `0x81b4bf45...` (22 / 29.200), `0x96a78d19...` (6 / 11.400), `0xba0fba22...` (4 / 2.200), `0x6f473d0d...` (4 / 3.100) - 227.000 OBRAIN phá hủy không hồi vào `0x...dEaD`, luôn đúng giá cấp. Khoảng cách giữa các tư duy: trung vị ~20 giây, trung bình 99,6 phút, tối đa 69,6 giờ; CV 5,11, **burstiness 0,672** - một chế độ dinh dưỡng burst mạnh, cấu trúc phiên (Hình 6A). Đóng góp của chính sinh vật - rò, ngưỡng, reset - là thứ biến burstiness đó thành sự xen kẽ của mục 3.6.

## 4. Bàn luận

**Sự chính xác của mẫu vật bất tử.** Tính chất cuộc điều tra này xác lập là tính nền bảo chứng và twin xác nhận: toàn bộ đời đã ghi của sinh vật tất định và tái tạo được tới byte. Dẫn bởi 74 từ truyền vào, mẫu vật tham chiếu tái sinh mọi vector danh tính xung và fold trạng thái cuối chính xác - và getter của hợp đồng đồng thuận tại mọi kỷ nguyên kiểm. Tuyên bố của kho - giải phẫu-như-phép-tính, chạy trong đồng thuận - do đó không phải tuyên mà là đo, across toàn bộ phát sinh cá thể sớm. Mọi tư duy tương lai kế thừa cùng tính kiểm toán, mãi mãi, trước mọi đối thủ.

**Một sinh lý giác quan đang hoạt động.** Với liều một đợt giới hạn 16.320 lượng tử trước ngưỡng 12.800, số học điểm cố định dự đoán chính xác điều điều tra thấy: phóng cột (cột mãng phóng ở mọi liều), chiêu mộ đơn điệu theo liều (4,90 / 7,39 / 11,17), tổng hợp thời gian vượt ngưỡng across các đợt (tick 18-19), quỹ đạo khóa trạng thái dưới kích thích lặp (4, 12, 4, 12). Điện tích dư của thượng bì - cell 3 vận chuyển 4.402 lượng tử across các ngày - cấu thành nền trí nhớ ngắn hạn của mẫu vật, và thấy trực tiếp trong bản ghi mạn tính.

**Chân trời chất vấn.** Nền điều tra làm các câu hỏi kế trở nên chính xác, và mỗi câu chạy được bởi bất kỳ ai giữ OBRAIN: (E1) nuôi cấp-2 bền một kênh - quỹ đạo khóa, hay cột láng giềng gia nhập khi phần dư tích? (E2) từ truyền vào ghép - đóng gói cho phép đợt đa kênh chưa ai dựng; (E3) chân trời phóng - các điện tích hạ nguồn mạnh nhất đếm được từ `tapes/` hôm nay, nên liều mà hoạt động rời thượng bì cảm giác lần đầu là một con số, chờ nhà tài trợ. Mỗi kết quả sẽ đến như một sự kiện `BrainState` - đóng dấu, fold, và tái chạy được với twin cư ngụ trong kho này.

## 5. Dữ liệu, mã và tái lập

Mọi artifact cần để suy lại nghiên cứu này đóng gói trong kho:

| Artifact | Đường dẫn |
|---|---|
| bản điều tra, đọc máy được (74 tư duy) | `data/brainstate_census.csv`, `data/brainstate_census.json` |
| 74 từ truyền vào, theo thứ tự | `data/poke_inputs.txt` |
| quét lại đồng thuận và so với bản điều tra | `python3 tools/verify_census.py` (chỉ stdlib) |
| tái chạy cả đời mẫu vật, từng byte | `python3 tools/verify_twin.py --fired $(cat data/poke_inputs.txt)` (numpy) |
| lần chạy twin của nghiên cứu này | `verification/twin_replay.log` |
| chứng minh đồng nhất byte dây nối | `python3 tools/verify_tapes.py` |
| bảng cấu trúc tế bào (5 byte/cell) | `annotations/neuron_annotations.{bin,json}` |
| hình | `figures/fig01..fig06` |
| checksum mọi artifact | `SHA256SUMS` |

Sự kiện chuỗi: Arc mainnet (5042), não `0xaef83c5b8742da5e3228930bc6084adcf0539ccd`; sự kiện bằng `eth_getLogs` chunk 9.999 khối từ khối 21.181.651; archive `eth_call` selector `0x9588eca2` (stateRoot) tại khối tick 40/54/64 và đầu. Nguồn gốc: BANC v888 (Bates et al., *Nature* 656, 957-970, 2026; doi:10.1038/s41586-026-10735-w). Biên lai mẫu: tick 5 tx `0x0cd97a330c9f30c96c27ad2d68b3dbeda89fda53512fe4624a0a3cd0e33d63f8`; tick 19 tx `0x60e57f9a540a8f9d67...`; tick 64 tx `0x488311c4a0c5c08b15...`.

## Phụ lục A - bản điều tra

Mỗi dòng một tư duy: kích thích truyền vào (kênh, cấp, OBRAIN chuyển hóa), phản ứng (cell phóng, phép toán synapse đăng ký, danh tính xung đầu), và biên lai. Giao dịch đầy đủ trên trình khám phá Arc theo khối của tick.

| tick | UTC | kênh | cấp | OBRAIN | phóng | syn | danh tính đầu | tx |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-09-16 15:54:40 | 0 | 1 | 1,000 | 0 | 0 | - | 0x479768c322… |
| 2 | 2026-09-16 15:56:58 | 26 | 0 | 100 | 4 | 8 | 25, 85, 145, 205 | 0xb1aba1468c… |
| 3 | 2026-09-16 17:00:52 | 19 | 0 | 100 | 4 | 7 | 18, 78, 138, 198 | 0x0c9d673fbb… |
| 4 | 2026-09-16 17:36:53 | 48 | 0 | 100 | 4 | 5 | 47, 107, 167, 227 | 0x8fa05531f4… |
| 5 | 2026-09-19 15:13:19 | 1 | 2 | 10,000 | 10 | 18 | 0, 1, 60, 61, 120, 121 … | 0x0cd97a330c… |
| 6 | 2026-09-20 03:28:30 | 21 | 0 | 100 | 8 | 11 | 19, 20, 79, 80, 139, 140 … | 0xca8ff75f90… |
| 7 | 2026-09-20 03:28:57 | 21 | 0 | 100 | 4 | 6 | 20, 80, 140, 200 | 0x755d16b643… |
| 8 | 2026-09-20 03:30:06 | 21 | 1 | 1,000 | 8 | 11 | 19, 20, 79, 80, 139, 140 … | 0xa11feef715… |
| 9 | 2026-09-20 03:30:26 | 21 | 1 | 1,000 | 8 | 14 | 20, 21, 80, 81, 140, 141 … | 0xa77991b993… |
| 10 | 2026-09-20 03:56:25 | 12 | 0 | 100 | 5 | 9 | 11, 71, 131, 191, 251 | 0x60802806e9… |
| 11 | 2026-09-20 03:57:51 | 52 | 0 | 100 | 4 | 3 | 51, 111, 171, 231 | 0x09005fcdb7… |
| 12 | 2026-09-20 03:57:54 | 37 | 1 | 1,000 | 4 | 8 | 36, 96, 156, 216 | 0x96913850ba… |
| 13 | 2026-09-20 10:27:42 | 34 | 1 | 1,000 | 4 | 8 | 33, 93, 153, 213 | 0x366ec9760d… |
| 14 | 2026-09-20 10:27:50 | 43 | 1 | 1,000 | 4 | 6 | 42, 102, 162, 222 | 0x9d7dab821d… |
| 15 | 2026-09-20 10:28:50 | 28 | 1 | 1,000 | 8 | 13 | 26, 27, 86, 87, 146, 147 … | 0xbee24ab339… |
| 16 | 2026-09-20 10:29:15 | 31 | 1 | 1,000 | 8 | 8 | 29, 30, 89, 90, 149, 150 … | 0x0254aee9bb… |
| 17 | 2026-09-20 10:33:02 | 9 | 1 | 1,000 | 5 | 10 | 8, 68, 128, 188, 248 | 0x1bddbcd9fc… |
| 18 | 2026-09-20 10:34:31 | 0 | 1 | 1,000 | 0 | 0 | - | 0x0bb4aed33a… |
| 19 | 2026-09-20 10:34:36 | 0 | 1 | 1,000 | 5 | 10 | 0, 60, 120, 180, 240 | 0x60e57f9a54… |
| 20 | 2026-09-20 10:34:39 | 19 | 1 | 1,000 | 12 | 17 | 17, 18, 19, 77, 78, 79 … | 0xb106c2f72d… |
| 21 | 2026-09-20 10:34:44 | 4 | 1 | 1,000 | 10 | 19 | 2, 3, 62, 63, 122, 123 … | 0x604eeb1fd4… |
| 22 | 2026-09-20 10:34:48 | 4 | 1 | 1,000 | 10 | 19 | 3, 4, 63, 64, 123, 124 … | 0x7741278aa4… |
| 23 | 2026-09-20 10:34:52 | 35 | 1 | 1,000 | 8 | 12 | 34, 35, 94, 95, 154, 155 … | 0x571349731e… |
| 24 | 2026-09-20 10:34:59 | 16 | 1 | 1,000 | 5 | 8 | 15, 75, 135, 195, 255 | 0x359fd622d4… |
| 25 | 2026-09-20 10:35:07 | 7 | 1 | 1,000 | 15 | 26 | 5, 6, 7, 65, 66, 67 … | 0x195c7a6be8… |
| 26 | 2026-09-20 10:35:10 | 1 | 1 | 1,000 | 5 | 10 | 0, 60, 120, 180, 240 | 0x853376e254… |
| 27 | 2026-09-20 10:38:20 | 32 | 2 | 10,000 | 12 | 21 | 31, 32, 33, 91, 92, 93 … | 0x1e81361cdf… |
| 28 | 2026-09-20 10:44:37 | 15 | 1 | 1,000 | 5 | 8 | 14, 74, 134, 194, 254 | 0xec27a8c1e3… |
| 29 | 2026-09-20 10:44:46 | 15 | 1 | 1,000 | 15 | 24 | 13, 14, 15, 73, 74, 75 … | 0x715a9b56a6… |
| 30 | 2026-09-20 10:49:10 | 16 | 1 | 1,000 | 9 | 14 | 15, 16, 75, 76, 135, 136 … | 0x7ca4b4f115… |
| 31 | 2026-09-20 14:54:55 | 3 | 1 | 1,000 | 10 | 17 | 1, 2, 61, 62, 121, 122 … | 0x551ee2c13e… |
| 32 | 2026-09-20 14:57:14 | 48 | 0 | 100 | 8 | 11 | 46, 47, 106, 107, 166, 167 … | 0x4da88a602c… |
| 33 | 2026-09-20 14:57:40 | 48 | 1 | 1,000 | 4 | 5 | 47, 107, 167, 227 | 0xd55075b49b… |
| 34 | 2026-09-20 14:58:18 | 48 | 1 | 1,000 | 12 | 19 | 46, 47, 48, 106, 107, 108 … | 0x03300afae5… |
| 35 | 2026-09-20 15:00:24 | 20 | 1 | 1,000 | 4 | 5 | 19, 79, 139, 199 | 0x7eec882790… |
| 36 | 2026-09-20 15:00:34 | 20 | 1 | 1,000 | 12 | 18 | 18, 19, 20, 78, 79, 80 … | 0xcf6b4f53d9… |
| 37 | 2026-09-20 15:00:38 | 20 | 1 | 1,000 | 4 | 5 | 19, 79, 139, 199 | 0xbed1c8fe8f… |
| 38 | 2026-09-20 15:00:43 | 20 | 1 | 1,000 | 12 | 18 | 18, 19, 20, 78, 79, 80 … | 0x93b1e4a0f7… |
| 39 | 2026-09-20 15:04:32 | 20 | 2 | 10,000 | 8 | 11 | 19, 20, 79, 80, 139, 140 … | 0x9997c9ec5d… |
| 40 | 2026-09-20 15:04:45 | 20 | 2 | 10,000 | 12 | 18 | 18, 19, 20, 78, 79, 80 … | 0xd8ea6f3b13… |
| 41 | 2026-09-21 07:40:52 | 10 | 1 | 1,000 | 10 | 19 | 9, 10, 69, 70, 129, 130 … | 0x3a7c98e592… |
| 42 | 2026-09-21 07:40:56 | 10 | 1 | 1,000 | 10 | 19 | 8, 9, 68, 69, 128, 129 … | 0x1fed29c864… |
| 43 | 2026-09-21 07:41:01 | 52 | 1 | 1,000 | 8 | 10 | 50, 51, 110, 111, 170, 171 … | 0x3f4b1253ae… |
| 44 | 2026-09-21 07:41:09 | 2 | 1 | 1,000 | 5 | 8 | 1, 61, 121, 181, 241 | 0xc32cb52a4f… |
| 45 | 2026-09-21 07:41:16 | 2 | 1 | 1,000 | 15 | 27 | 0, 1, 2, 60, 61, 62 … | 0x6ff6cba397… |
| 46 | 2026-09-21 07:41:20 | 36 | 1 | 1,000 | 4 | 6 | 35, 95, 155, 215 | 0x0e24767a5c… |
| 47 | 2026-09-21 07:41:28 | 31 | 1 | 1,000 | 4 | 3 | 30, 90, 150, 210 | 0x696e1f2db2… |
| 48 | 2026-09-21 07:41:32 | 22 | 1 | 1,000 | 4 | 8 | 21, 81, 141, 201 | 0xe6e24f16f4… |
| 49 | 2026-09-21 07:41:35 | 13 | 1 | 1,000 | 10 | 18 | 11, 12, 71, 72, 131, 132 … | 0x71eb3defb4… |
| 50 | 2026-09-21 12:44:35 | 41 | 0 | 100 | 4 | 8 | 40, 100, 160, 220 | 0x9f641c7c86… |
| 51 | 2026-09-21 12:44:53 | 9 | 1 | 1,000 | 5 | 10 | 8, 68, 128, 188, 248 | 0x171a1e28db… |
| 52 | 2026-09-21 12:45:25 | 22 | 1 | 1,000 | 12 | 22 | 20, 21, 22, 80, 81, 82 … | 0x32fad15143… |
| 53 | 2026-09-21 12:46:30 | 28 | 1 | 1,000 | 4 | 7 | 27, 87, 147, 207 | 0x865a4ee64b… |
| 54 | 2026-09-21 12:47:37 | 24 | 0 | 100 | 4 | 8 | 23, 83, 143, 203 | 0x59b87debb3… |
| 55 | 2026-09-21 16:45:17 | 29 | 2 | 10,000 | 8 | 10 | 28, 29, 88, 89, 148, 149 … | 0xae20a56e06… |
| 56 | 2026-09-21 16:45:24 | 29 | 2 | 10,000 | 12 | 17 | 27, 28, 29, 87, 88, 89 … | 0xbcb3296430… |
| 57 | 2026-09-21 16:45:28 | 29 | 2 | 10,000 | 8 | 10 | 28, 29, 88, 89, 148, 149 … | 0xd401fb9986… |
| 58 | 2026-09-21 16:51:48 | 15 | 2 | 10,000 | 15 | 24 | 13, 14, 15, 73, 74, 75 … | 0xc0d5a53d87… |
| 59 | 2026-09-21 16:51:53 | 15 | 2 | 10,000 | 10 | 16 | 14, 15, 74, 75, 134, 135 … | 0xde915b9676… |
| 60 | 2026-09-21 16:51:59 | 15 | 2 | 10,000 | 15 | 24 | 13, 14, 15, 73, 74, 75 … | 0x3739bd0797… |
| 61 | 2026-09-21 16:52:05 | 15 | 2 | 10,000 | 10 | 16 | 14, 15, 74, 75, 134, 135 … | 0x0fa24cf48f… |
| 62 | 2026-09-21 16:52:14 | 15 | 2 | 10,000 | 15 | 24 | 13, 14, 15, 73, 74, 75 … | 0xdb583fb8cc… |
| 63 | 2026-09-21 16:52:25 | 15 | 2 | 10,000 | 10 | 16 | 14, 15, 74, 75, 134, 135 … | 0xa0e4aeb08a… |
| 64 | 2026-09-21 16:53:13 | 15 | 2 | 10,000 | 19 | 30 | 13, 14, 15, 16, 73, 74 … | 0x488311c4a0… |
| 65 | 2026-09-21 16:58:21 | 17 | 2 | 10,000 | 8 | 11 | 16, 17, 76, 77, 136, 137 … | 0x8bdcbbb130… |
| 66 | 2026-09-21 17:01:29 | 47 | 1 | 1,000 | 4 | 6 | 46, 106, 166, 226 | 0xf893ad0ef3… |
| 67 | 2026-09-21 17:01:30 | 17 | 2 | 10,000 | 13 | 19 | 15, 16, 17, 75, 76, 77 … | 0x46bad7d8f4… |
| 68 | 2026-09-21 17:03:11 | 16 | 1 | 1,000 | 5 | 8 | 15, 75, 135, 195, 255 | 0xc3ce053040… |
| 69 | 2026-09-21 17:03:21 | 19 | 1 | 1,000 | 8 | 12 | 17, 18, 77, 78, 137, 138 … | 0x55c04a7f19… |
| 70 | 2026-09-21 17:03:26 | 19 | 1 | 1,000 | 8 | 12 | 18, 19, 78, 79, 138, 139 … | 0xfbad83a523… |
| 71 | 2026-09-21 17:04:56 | 16 | 1 | 1,000 | 14 | 22 | 14, 15, 16, 74, 75, 76 … | 0xa216057d9e… |
| 72 | 2026-09-21 17:05:05 | 40 | 2 | 10,000 | 8 | 13 | 39, 40, 99, 100, 159, 160 … | 0xe4f6ae544d… |
| 73 | 2026-09-21 17:05:32 | 34 | 2 | 10,000 | 8 | 14 | 33, 34, 93, 94, 153, 154 … | 0xf222c026b8… |
| 74 | 2026-09-21 17:05:48 | 20 | 1 | 1,000 | 4 | 5 | 19, 79, 139, 199 | 0x4dc0506926… |
## Phụ lục B - sự kiện chuỗi lúc đóng điều tra (2026-09-22)

| Sự kiện | Giá trị |
|---|---|
| hợp đồng não | `0xaef83c5b8742da5e3228930bc6084adcf0539ccd` (Arc 5042) |
| tick / niêm phong | 74 / true |
| cell / ngưỡng / cảm giác / đoạn / tape | 169.088 / 12.800 / 256 / 64 / 85 |
| config hash | `0xef009ad9054213480da1bbce5954163e5e14a0bcef8145fda42c9621610e7d67` |
| stateRoot() tại đầu | `0xe415d94744ee6447edcce1ae9447352c457b993a61277ab3b9dda17bd5483412` (= twin, đẳng cấu byte) |
| tư duy / phóng / cell riêng | 74 / 590 / 192 (danh tính <= 255, 100% não trung ương) |
| phép toán synapse đăng ký | 942 tổng, tối đa 30 mỗi tư duy |
| OBRAIN chuyển hóa | 227.000 bởi 5 ví, luôn đúng giá cấp |
