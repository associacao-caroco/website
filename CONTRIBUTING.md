# Como propor alterações ao site

Nada vai para o site diretamente. O `main` está protegido: toda a alteração passa por um
pull request e só é publicada quando o Luca o aprova e faz merge. O merge é o que dispara
a publicação em <https://caroco.pt>.

Não é preciso saber programar. Basta descrever o que quer mudar.

## Pedir uma alteração

Tudo pelo site do GitHub, no navegador:

1. Abra <https://github.com/associacao-caroco/website/tree/main/pedidos>.
2. Clique em **Add file**, depois em **Create new file**.
3. Dê ao ficheiro um nome com data e assunto, por exemplo
   `pedidos/20260815-noticia-residencia.md`.
4. Escreva o pedido. Use o modelo em [`pedidos/MODELO.md`](pedidos/MODELO.md) como guia.
   Diga em que página, o que deve mudar, e o texto novo se já o tiver. Português ou
   inglês, tanto faz: o site é bilingue e a tradução é feita depois.
5. Em baixo, clique em **Propose new file**. Se o GitHub avisar que vai criar uma cópia
   (fork) do repositório na sua conta, aceite: é normal e é assim que funciona para quem
   não tem permissão de escrita.
6. Na página seguinte, clique em **Create pull request**, e outra vez para confirmar.
   Deixe a opção **Allow edits by maintainers** marcada, é o que permite aplicar as
   alterações no seu pedido.

Está feito. O pedido fica registado como pull request e recebe resposta aí.

## O que acontece depois

O Luca pega no mesmo pull request, aplica as alterações no site (HTML, CSS, imagens) no
mesmo branch, e volta a comentar. Se estiver conforme o pedido, faz merge e o site é
publicado poucos minutos depois. Se houver dúvidas, ficam no pull request.

Pode responder e pedir correções antes do merge. É esse o objetivo de passar por aqui.

## Verificações automáticas

Vai ver no pull request um conjunto de verificações a correr. São nossas, verificam coisas
como as duas línguas estarem em sincronia, e não têm nada a ver com o seu pedido: um
pedido em `pedidos/` nunca as faz falhar. Se aparecer uma cruz vermelha depois de as
alterações serem aplicadas, a explicação está na própria página do pull request, em
português e em inglês, e é o Luca que a resolve.

## Fotografias e documentos

Ficheiros grandes não se enviam bem pelo navegador. Envie-os por email para
<info@caroco.pt> e refira no pedido que os enviou. Nunca coloque no repositório
palavras-passe, tokens ou dados pessoais de terceiros: o repositório é público.

---

# How to propose changes to the site

Nothing goes live directly. `main` is protected: every change goes through a pull request
and is published only once Luca approves it and merges. The merge is what triggers a
deploy to <https://caroco.pt>.

You do not need to write code. Describing the change is enough.

## Requesting a change

All of this happens on the GitHub website, in your browser:

1. Open <https://github.com/associacao-caroco/website/tree/main/pedidos>.
2. Click **Add file**, then **Create new file**.
3. Name the file with a date and a subject, for example
   `pedidos/20260815-noticia-residencia.md`.
4. Write the request, using [`pedidos/MODELO.md`](pedidos/MODELO.md) as a guide. Say
   which page, what should change, and the new text if you already have it. Portuguese or
   English is fine: the site is bilingual and translation happens later.
5. At the bottom, click **Propose new file**. If GitHub warns that it will create a copy
   (a fork) of the repository under your account, accept it: that is normal for anyone
   without write access.
6. On the next screen, click **Create pull request**, then again to confirm. Leave
   **Allow edits by maintainers** ticked, that is what lets the changes be applied to your
   request.

That is all. The request now exists as a pull request and gets answered there.

## What happens next

Luca takes that same pull request, applies the actual site changes (HTML, CSS, images) on
the same branch, and comments back. If it matches the request, he merges and the site
updates within a few minutes. Any questions stay on the pull request.

You can reply and ask for corrections before the merge. That is the point of going
through here.

## Automated checks

You will see a set of checks running on the pull request. They are ours, they verify things
like both languages staying in step, and they have nothing to do with your request: a file
in `pedidos/` can never make them fail. If a red cross appears after the changes have been
applied, the explanation is on the pull request page itself, in Portuguese and in English,
and it is Luca's to sort out.

## Photos and documents

Large files do not upload well through the browser. Email them to <info@caroco.pt> and
mention in the request that you have sent them. Never put passwords, tokens, or other
people's personal data in the repository: it is public.
