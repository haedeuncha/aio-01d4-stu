# 치이카와 · 작은 친구들

Windows 10/11용 Electron + TypeScript + Vite 데스크톱 캐릭터 오버레이입니다. 제공받은 Chiikawa_Assets.zip의 42개 PNG를 `public/assets` 아래 원래 구조로 보존했습니다. 이미지 생성이나 대체 그림을 사용하지 않습니다.

## 설치와 실행

Node.js 22.15 이상, Windows 10/11, 인터넷 연결(최초 의존성 및 Electron 다운로드)이 필요합니다. VS Code와 Git은 선택입니다. 프로젝트 폴더에서 PowerShell을 열어 실행하세요.

```powershell
npm ci
npm run dev
```

`dev`는 Vite와 실제 Electron을 함께 실행합니다. 렌더러 변경은 자동 반영되며 메인 프로세스 변경 후에는 재시작해야 합니다. 처음에는 작업표시줄 위에 친구들이 나타납니다. 트레이 아이콘을 오른쪽 클릭하여 설정·모드·종료 메뉴를 엽니다. 더블 클릭하면 설정 창이 열립니다.

```powershell
npm test
npm run build
npm run desktop
```

`desktop`은 빌드된 파일로 실행합니다. `npm run dev:web`은 브라우저 미리보기만 실행합니다. 웹 미리보기에는 Windows 창 추적·전역 단축키·트레이·클릭 통과가 없습니다. 서버 주소는 `http://127.0.0.1:5173`입니다. 앱 중복 실행은 기존 앱 설정 창을 표시합니다.

설정은 프로젝트 `.runtime/settings.json`에 원자적으로 저장합니다. 실행 로그는 `.runtime/desktop.log`입니다. 경로에 쓰기 권한이 있어야 합니다. 최초 Electron 다운로드가 실패했다면 네트워크 연결 후 다시 실행하세요. 제한된 환경에서는 다음 캐시 경로를 사용할 수 있습니다.

```powershell
$env:npm_config_cache = Join-Path $PWD '.npm-cache'
$env:electron_config_cache = Join-Path $PWD '.electron-cache'
```

## 사용법

| 조작 | 동작 |
|---|---|
| Ctrl+Alt+M | 자유 → 포인터 → 천장 → 낮잠 순환 |
| Ctrl+Alt+G | 각 모니터 바닥으로 친구 모으기 |
| Ctrl+Alt+H | 숨김/표시 |
| Ctrl+Alt+Q | 앱 종료 |
| 캐릭터 클릭·드래그 | 그룹 따라오기 중지, 캐릭터 이동 |
| 트레이/설정의 다시 따라오기 | 포인터 모드 및 그룹 추적 재개 |

자유 모드에서는 바닥 산책·간식·휴식을 반복하며 적합한 창이 있으면 창 옆으로 점프합니다. 약 1초 매달린 뒤 0.9초간 벽타기 3프레임을 재생하고 창 위 걷기로 복귀합니다. 창 이동은 보간해서 따라가고 최소화·종료로 창이 사라지면 바닥으로 내려옵니다. 전체화면 전경 창을 감지하면 자유 모드에서도 천장으로 이동합니다. 천장 이미지는 이미 거꾸로 그려져 있어 다시 뒤집지 않습니다.

설정 창에서 60/30fps와 캐릭터 크기(64~160 DIP)를 변경할 수 있습니다. 모든 캐릭터는 투명 여백을 제외한 최대 변의 크기를 동일하게 맞춥니다. 낮잠 포즈의 높이가 걷기 포즈와 다른 것은 원본 비율을 보존한 결과입니다.

## Assets와 프레임

| 경로 | 배열 | 프레임 크기 |
|---|---|---|
| `assets/brand/` | 로고·트레이 아이콘 | 원본 |
| `assets/characters/` | 이전 참조 이미지 | 보존, 렌더링 미사용 |
| `assets/v2/characters/` | 4열 × 2행 | 대체로 192×256, 우사기 221.75×222 |
| `assets/v2/walk-cycles/` | 3열 × 3행 | 치이카와 216×202.33, 하치와레 210.33×208, 우사기 210.67×207.67, 모몽가 256×170.67 |
| `assets/v2/hang-left/`, `hang-right/`, `hang-ceiling/` | 3열 × 1행 | 362×362 |
| `assets/v2/climb/`, `lying/` | 3열 × 1행 | 682.67×682 |

정확한 파일별 원본 크기와 행·열 정보는 `public/assets/sprite-manifest.json`에 있습니다. `node scripts/assets-manifest.mjs`로 재생성합니다. 정수가 아닌 셀 경계는 `round(index * dimension / count)`로 계산합니다. 각 프레임에서 알파 >32인 픽셀의 경계를 찾아 자르고, 최대 192px 캔버스에 캐시합니다. 28개 시트를 하나씩 디코딩한 뒤 원본 이미지 참조를 해제합니다. 클릭 판정도 캐시한 픽셀의 알파를 사용합니다. 걷기 방향이 왼쪽인 경우와 오른쪽 벽타기에만 필요한 수평 반전을 적용합니다.

## 구조와 보안

- `electron/main.ts`: 모니터별 투명·프레임리스·비포커스 오버레이, 트레이, 전역 단축키, 설정, DPI 변환.
- `electron/preload.ts`: 한정된 IPC API. `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`.
- `scripts/windows.ps1`: 숨겨진 단일 PowerShell 프로세스에서 Win32/DWM 창 목록을 300ms마다 읽습니다. 창 내용·제목은 수집하지 않고 위치·크기·핸들·전경 여부만 전달합니다.
- `src/engine.ts`: 상태 머신과 좌표 보간. `src/sprites.ts`: 순차 디코딩·투명 여백 제거. `src/main.ts`: Canvas/설정 UI.
- 투명 영역은 `setIgnoreMouseEvents`로 통과시키며 커서와 캐릭터 알파를 비교해 입력을 전환합니다. 오버레이는 `showInactive`와 `focusable:false`를 사용하고 설정 창만 포커스를 받습니다.
- 렌더링은 requestAnimationFrame을 사용합니다. 숨김 상태에서는 rAF와 커서 전송을 멈춥니다. 창 추적 프로세스는 유지합니다.
- `.tmp`, `.temp`, `.part`, `.crdownload`는 개발 감시에서 제외합니다.

## 제한사항 및 실제 기기 검증

- 모니터마다 네 캐릭터를 표시합니다. 모니터 사이에 단일 그룹을 이동시키는 방식은 구현하지 않았습니다. 디스플레이 추가·제거·배율 변경 시 오버레이를 재생성하므로 위치는 초기화됩니다.
- 창 추적은 약 300ms 간격입니다. 임의 모양 창, 다른 창에 가려진 경계의 정밀 판정, 화면 여러 개를 가로지르는 창의 벽타기는 지원 범위가 제한적입니다. 완전히 해당 모니터 안에 들어온 창을 새 벽타기 대상으로 선택합니다.
- 관리자 권한 앱, 독점 전체화면 게임, 보안 데스크톱에서는 오버레이·마우스 전달이 제한될 수 있습니다. 창 추적 실패 시 바닥 산책은 계속됩니다. PowerShell 실행을 막는 조직 정책이 있는 환경은 별도 확인이 필요합니다.
- 클릭 통과 전환은 프레임/커서 갱신 간격의 지연이 있으며, 매우 빠른 클릭과 드래그, 혼합 DPI 모니터에서 실기 검증이 필요합니다. 단축키가 다른 앱에 이미 등록되어 있으면 로그에 남습니다.
- 설치 마법사, 코드 서명, 자동 업데이트, 시작 프로그램 등록은 포함하지 않았습니다. `npm run build`는 실행용 JS/웹 리소스를 만들며 배포 설치 EXE를 만들지 않습니다.
- 자동 테스트는 설정 검증, 매달림→3프레임 벽타기→걷기, 창 소멸 후 복귀, 음수 모니터 좌표, 따라오기 중지/재개, 천장·낮잠 보간을 확인합니다. Windows의 클릭 통과·포커스·트레이·작업표시줄·DPI까지 보증하지 않습니다.

실기 확인: 메모장 등 일반 창을 이동·최대화·최소화·닫기, 캐릭터 밖 클릭, 드래그와 다시 따라오기, 모든 단축키, 트레이 종료, 앱 재실행 후 설정 유지, 다중 모니터/혼합 DPI를 확인하세요.

이미지의 배포·상업 이용 권리는 사용자 제공 원본의 이용 조건을 따릅니다.

Electron API 참고: [BrowserWindow](https://www.electronjs.org/docs/latest/api/browser-window/), [screen](https://www.electronjs.org/docs/latest/api/screen).
