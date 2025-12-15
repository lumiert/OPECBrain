# OPECBrain
## [📥 Download](https://github.com/lumiert/OPECBrain/releases/tag/1.0)
Aplicação Python que roda na bandeja do sistema (traybar) e permite registrar rapidamente objetos com status e timestamp.

Como usar:
- Extraia o .zip;
- Abra o .exe;
- Atalho CTRL + 0;
- O app roda na tray.

Funcionalidades:
- Ícone na tray com menu: Histórico, Novo registro, Sair.
- Atalho global `Ctrl+0` para abrir a barra de adição centralizada.
- Registro salvo em `common/data/historico.json` com campos: Objeto, Data e Hora, Status.
- Tela de Histórico exibindo tabela com os registros.
- Campo aceita "nome do objeto | status" para enviar em uma linha. Ex.: `Contrato 123 | pronto`.

Requisitos:
- Python 3.10+ no Windows.
- `tkinter` (parte da instalação padrão do Python para Windows).
- Pacotes: pystray, Pillow, keyboard.

Instalação:
```powershell
python -m pip install -r requirements.txt
```

Execução:
```powershell
python .\main.py
```

Observações:
- UI moderna com `ttkbootstrap` tema `cyborg` (dark) e janelas em "always-on-top" para acesso rápido.
- Em alguns sistemas, o `keyboard` pode requerer privilégios de administrador para registrar hotkeys globais. Se o atalho não funcionar, tente abrir o terminal como Administrador.
- O arquivo de histórico é criado automaticamente se não existir.
- Ícones Phosphor: baixe ícones PNG de https://phosphoricons.com e coloque em `common/icons` (ex.: `brain.png`, `clipboard-text.png`). O app detecta automaticamente se disponíveis.
