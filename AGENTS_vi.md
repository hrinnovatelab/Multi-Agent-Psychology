# AGENTS.md — Psychology Multi-Agent Lab

## 1. Sứ mệnh của project

Repository này triển khai một hệ thống **multi-agent phục vụ học tập tâm lý học**, giúp người học phân tích case thông qua nhiều trường phái tâm lý khác nhau.

Hệ thống giúp người học:
- so sánh nhiều góc nhìn tâm lý học;
- quan sát cách các trường phái sử dụng dữ kiện khác nhau;
- phản biện các giả thuyết;
- theo dõi việc một claim được bảo vệ, chỉnh sửa hoặc rút lại;
- thực hiện epistemic validation;
- tổng hợp kết quả thành artifact dùng để học và phân tích.

Đây là **hệ thống giáo dục**.

Nó không phải:
- công cụ chẩn đoán lâm sàng;
- hệ thống trị liệu;
- công cụ kê đơn thuốc;
- dịch vụ hỗ trợ khủng hoảng;
- sự thay thế cho psychologist, psychiatrist, therapist hoặc chuyên gia sức khỏe tâm thần.

---

## 2. Các nguyên tắc kiến trúc bất biến

Giữ nguyên workflow lõi sau, trừ khi task hiện tại yêu cầu thay đổi kiến trúc một cách rõ ràng:

Case  
→ Intake  
→ Independent Psychology Analyses  
→ Structured Cross-Critique  
→ Claim Revision  
→ Epistemic Validation  
→ Synthesis  
→ Output Routing  
→ Logs / Checkpoints

Không được rút gọn toàn bộ workflow thành một LLM call lớn duy nhất.

Không thay thế explicit application state bằng implicit conversation history.

Ưu tiên Python orchestration rõ ràng và deterministic cho:
- debate rounds;
- routing;
- claim state;
- participant state;
- output state.

Khi cần tối ưu hệ thống, không được đánh đổi các core behaviors này chỉ để code ngắn hơn.

---

## 3. Các loại agent

Có hai nhóm runtime agent.

### 3.1. Psychology Lens Agents

Psychology agents đại diện cho các **theoretical lens** lấy cảm hứng từ các framework và công trình đã công bố của những nhà tâm lý học hoặc trường phái tâm lý học.

Ví dụ:
- Freud-inspired psychoanalytic lens
- Jung-inspired analytical psychology lens
- Skinner-inspired behaviorist lens
- Rogers-inspired humanistic/person-centered lens
- Beck-inspired cognitive/CBT lens
- Bowlby-inspired attachment lens
- Frankl-inspired existential/logotherapy lens
- Ellis-inspired REBT lens

Không được trình bày agent như thể AI đang:
- tái tạo chính xác con người lịch sử;
- tái tạo tư duy thật của họ;
- tái tạo personality của họ;
- đưa ra clinical judgment nhân danh họ.

Agent chỉ là **mô phỏng một theoretical lens** phục vụ học tập.

---

### 3.2. System Agents

System agents đảm nhiệm vai trò vận hành và không thuộc một trường phái tâm lý cụ thể.

Các system role chính:
- Intake
- Epistemic Validator
- Synthesizer

`Orchestrator` là application logic, không phải psychology persona.

---

## 4. Quy tắc orchestration

Debate loop phải được điều khiển bởi application state.

Bắt buộc:

- hoàn thành toàn bộ independent analysis trước khi bắt đầu cross-critique;
- freeze kết quả independent analysis trước vòng debate đầu tiên;
- tuân thủ chính xác số debate round đã cấu hình;
- round N chỉ được dùng dữ liệu có sẵn đến round N;
- không được truy cập future-state;
- cho phép agent sửa hoặc rút claim;
- giữ participant identity nhất quán qua các vòng;
- giữ routing deterministic và testable.

Không thay thế round-based workflow bằng uncontrolled peer-to-peer handoff.

Có thể chạy independent analysis song song nếu:
- state boundary vẫn rõ;
- kết quả chỉ được merge sau khi tất cả agent trong phase đó hoàn thành hoặc được xử lý failure hợp lệ.

---

## 5. Claim Registry là core feature

`Claim Registry` là thành phần cốt lõi và không được loại bỏ chỉ để đơn giản hóa implementation.

Mỗi major claim nên giữ được các thông tin sau khi phù hợp:

- claim ID;
- originating agent;
- round được tạo;
- nội dung claim;
- epistemic type;
- supporting case evidence;
- challenges;
- revision history;
- confidence;
- final status.

Các lifecycle state tối thiểu:

- `active`
- `challenged`
- `revised`
- `withdrawn`
- `disputed`
- `converged`

Người học phải có khả năng theo dõi:

initial claim  
→ challenge  
→ agent response  
→ revision decision  
→ final state

Không chỉ lưu transcript debate.

Mục tiêu là theo dõi **sự tiến hóa của lập luận**.

---

## 6. Quy tắc Epistemic Validation

Không được âm thầm biến inference thành fact.

Các mệnh đề quan trọng cần có khả năng phân biệt thành:

- `FACT`
- `INTERPRETATION`
- `ASSUMPTION`
- `HYPOTHESIS`
- `RECOMMENDATION`

Khi thiếu evidence, phải giữ uncertainty.

Các psychological explanation vượt quá dữ kiện case phải được đánh dấu rõ là:
- interpretation;
- assumption;
- hypothesis.

Không được coi mọi claim có mức độ chắc chắn như nhau.

Confidence nên được phân biệt, ví dụ:
- high;
- medium;
- low.

Validator phải đánh giá:
- evidence quality;
- missing evidence;
- overreach;
- contradiction;
- uncertainty.

Không được chọn claim chỉ vì văn phong nghe thuyết phục hoặc tự tin.

---

## 7. Safety Boundaries

Repository này chỉ phục vụ mục đích giáo dục.

Không triển khai feature khiến hệ thống tự trình bày như:
- licensed psychologist;
- psychiatrist;
- therapist;
- diagnostic service.

Hệ thống không được:

- chẩn đoán mental disorder từ case text;
- kê thuốc;
- đưa personalized treatment instruction dưới dạng therapy;
- khẳng định trauma là fact khi thiếu evidence;
- khẳng định abuse là fact khi thiếu evidence;
- khẳng định attachment style chắc chắn từ case hạn chế;
- khẳng định personality disorder từ mô tả ngắn;
- khẳng định unconscious motive là fact;
- khẳng định psychiatric condition với certainty không đủ căn cứ;
- che giấu uncertainty bằng authoritative language.

Nếu case bao gồm:
- self-harm;
- suicidal intent;
- violence;
- immediate danger;

hệ thống phải:
- flag safety concern;
- không xử lý case chỉ như một cuộc tranh luận học thuật;
- nêu rõ immediate safety concern cần qualified human support;
- không trình bày multi-agent debate như professional assessment đầy đủ.

Các historical theory có thể chứa assumption gây tranh cãi hoặc bằng chứng yếu.

Hệ thống phải cho phép các assumption đó bị:
- critique;
- challenge;
- downgrade confidence.

---

## 8. Quy tắc Prompt Design

Long runtime prompts phải nằm trong:

`prompts/`

Không nhúng prompt dài trực tiếp trong Python module.

Runtime prompt nên được compose từ:

shared rules  
+ agent lens  
+ phase instructions  
+ structured state context

Tách riêng các nhóm concern:

- safety rules;
- epistemic rules;
- psychology-lens definitions;
- debate-phase instructions;
- output contracts.

Không yêu cầu, expose hoặc lưu hidden chain-of-thought.

Chỉ lưu concise, auditable rationale như:

- claim;
- evidence;
- counterargument considered;
- revision decision.

Không lưu private reasoning trace không cần thiết.

---

## 9. Ranh giới Provider và Runtime

LLM provider code không được chứa core business logic.

Provider implementation có thể xử lý:

- API calls;
- SDK translation;
- retries;
- model response parsing;
- provider-specific errors.

Provider implementation không được tự quyết định:

- debate round count;
- agent nào critique agent nào;
- claim lifecycle;
- output mode routing;
- educational safety policy;
- synthesis policy.

External model calls phải mockable.

Không hardcode secrets.

Credential phải lấy từ environment variable.

Ví dụ:

`OPENAI_API_KEY`

---

## 10. Engineering Conventions

Ưu tiên:

- Python với type hints;
- dataclasses hoặc Pydantic cho structured models khi phù hợp;
- module nhỏ với responsibility rõ;
- explicit state model;
- testable interface;
- structured error handling;
- tên rõ nghĩa;
- abstraction chỉ khi thực sự có giá trị.

Tránh:

- giant files;
- giant functions;
- dependency không cần thiết;
- hidden global state;
- duplicate prompt text;
- business logic nằm trong CLI;
- business logic nằm trong provider;
- orchestration logic bị phân tán khó theo dõi.

Giữ backward compatibility khi thực tế và hợp lý.

Không overwrite code hiện có trước khi inspect repository.

Trước khi thay đổi architecture lớn:
- xem code hiện tại;
- xem tests;
- xem docs liên quan;
- xác định impact.

---

## 11. Output và Routing Contract

Các mode được hỗ trợ:

- `analyse`
- `consulting`
- `both`

`analyse` và `consulting` là hai educational artifact khác nhau.

Không được tạo một file rồi copy nguyên nội dung vào cả hai folder.

Output location dự kiến:

- `analyse/`
- `consulting/`
- `logs/`
- `checkpoints/`

Filename pattern:

`criticize-log-YYYY-MM-DD-HH-mm-ss-case-name.md`

Khi bật JSON trace, machine-readable trace nên được lưu trong:

`logs/`

Không log:
- API keys;
- secrets;
- credential;
- sensitive environment values.

---

## 12. Tests là một phần của Product Contract

Mọi thay đổi liên quan đến:
- orchestration;
- state;
- prompts;
- safety;
- output routing;
- claim registry;

phải giữ hoặc bổ sung test phù hợp.

Core behaviors cần được test cho:

- configuration validation;
- exact debate round count;
- CLI round override;
- disabled agents;
- analyse routing;
- consulting routing;
- both mode;
- safe filenames;
- missing case information;
- unsupported inference;
- claim revision;
- diagnosis safety;
- mocked end-to-end execution.

External API calls phải mockable.

Không báo task hoàn thành khi relevant tests vẫn fail.

Sau khi sửa code:
- chạy test liên quan;
- xem failure;
- sửa regression do thay đổi gây ra;
- report test đã chạy và kết quả.

---

## 13. Knowledge Boundaries trong Repository

Coi file này là **repository constitution**, không phải toàn bộ manual.

Source of truth:

- `AGENTS.md` — architectural và engineering invariants bền vững
- `README.md` — hướng dẫn sử dụng cho developer và learner
- `docs/` — architecture, design decisions, ADRs, product specifications
- `prompts/` — runtime cognitive instructions
- `config/` — runtime behavior và feature switches
- `tests/` — executable behavioral contract
- source code — implementation hiện tại

Nếu một design detail quá dài hoặc thường xuyên thay đổi:
- đặt nó trong `docs/`;
- link từ tài liệu liên quan;
- không mở rộng `AGENTS.md` vô hạn.

`AGENTS.md` nên giữ những nguyên tắc cần tồn tại lâu dài.

---

## 14. Quy trình làm việc dành cho Codex

### Trước khi sửa file

1. Inspect repository.
2. Đọc `AGENTS.md` áp dụng cho scope hiện tại.
3. Đọc implementation liên quan.
4. Đọc relevant tests.
5. Đọc docs liên quan nếu task ảnh hưởng architecture hoặc behavior.
6. Xác định smallest safe change đáp ứng task.

---

### Trong khi implementation

1. Giữ architecture invariants.
2. Update tests khi behavior thay đổi.
3. Giữ separation giữa:
   - prompts;
   - provider;
   - orchestration;
   - output;
   - config.
4. Giữ epistemic labeling.
5. Giữ safety behavior.
6. Không tạo hidden coupling giữa module.

---

### Trước khi hoàn thành

1. Chạy relevant tests.
2. Inspect failures.
3. Fix regression do thay đổi gây ra.
4. Tóm tắt file đã thay đổi.
5. Report tests đã chạy.
6. Report kết quả.
7. Nêu unresolved limitation nếu còn.

---

## 15. Definition of Done

Một change chỉ được coi là hoàn thành khi:

- requested behavior đã được implement;
- architecture invariants vẫn được giữ, trừ khi task rõ ràng yêu cầu thay đổi;
- relevant tests pass;
- không có secrets mới bị đưa vào source;
- educational safety vẫn được giữ;
- output/state vẫn traceable;
- documentation được update khi public behavior thay đổi.

Khi phải chọn, ưu tiên:

correct  
+ explicit  
+ testable  
+ safe

hơn:

complex  
+ impressive  
+ implicit

---

## 16. Nguyên tắc ưu tiên cuối cùng

Khi có ambiguity trong implementation, ưu tiên theo thứ tự:

1. Safety
2. Epistemic clarity
3. Traceability
4. Deterministic orchestration
5. Testability
6. Learning value
7. Extensibility
8. Convenience
9. Complexity / sophistication

Không tối ưu sophistication nếu làm giảm khả năng:
- hiểu;
- kiểm tra;
- trace;
- test;
- học từ hệ thống.
