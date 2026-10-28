# Café com SESMT – Kit de geração de e-books (BNSJ)

Kit de geração dos e-books **Café com SESMT** – BNSJ: checklists operacionais de segurança do trabalho em PDF vertical (formato 4:5, feito para ler no celular e postar no Instagram).

Cada e-book nasce de um arquivo de tema (`temas/NNN_tema.json`) e sai em PDF, com a identidade visual da BNSJ, checklist em cards e QR code.

## O que tem aqui
| Pasta/arquivo | Para que serve |
|---|---|
| `gerar_ebook.py` | O gerador: lê um tema e cria o PDF |
| `config_bnsj.json` | Dados fixos da marca: Instagram, livro, tagline |
| `temas/` | Um JSON por edição (17 temas: rolo compressor, içamento de cargas, trabalho em altura, escavações...) |
| `assets/` | Logos, fotos, símbolo e fontes (Bebas Neue e Oswald) |
| `LEIA-ME.txt` | Resumo técnico do kit |

## Como gerar um e-book
1. Instale o Python 3 e as bibliotecas: `pip install weasyprint "qrcode[pil]"`
   (no Windows, o WeasyPrint também precisa do GTK).
2. Na pasta do projeto, rode: `python gerar_ebook.py temas/001_rolo_compressor.json`
3. O PDF é criado na pasta `saida/`.

## Como criar um tema novo
Copie um arquivo de `temas/`, mude o número e o conteúdo (título, riscos, itens do checklist) e rode o gerador apontando para o novo arquivo.

## Observações
- As pastas `saida/` (PDFs prontos), `novos/` (rascunhos) e o arquivo `registro_edicoes.json` ficam só no computador da BNSJ e não são publicados.
- Licença: ainda não definida. Logos, fotos e textos são da BNSJ Assessoria; peça autorização antes de reutilizar.

**BNSJ Assessoria em SST** · Instagram [@bnsjassessoria_](https://instagram.com/bnsjassessoria_)