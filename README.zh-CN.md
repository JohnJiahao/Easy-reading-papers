# Easy-reading-papers

[English](README.md) | 简体中文

读论文通常要判断三件事：这篇跟手头的事有没有关系、值不值得花时间读、读完的东西以后还能不能找回来。

这个 skill 把三件事串起来：**先用低成本预览判断是否符合预期**；你决定读了，**再按 14 节做精读**；最后**按主题归档成 docx 报告，并把索引写好**。以后找到同类论文，也可以继续加进同一个主题。

一次最多 5 篇。PDF、DOI、arXiv 链接、网页都支持。

<strong style="color:#C00000;font-size:19px"><font color="#C00000" size="4">报告内容由 AI 生成，关键结论请对照原文核对。</font></strong>

## Table of Contents

- [先判断值不值得读](#preview)
- [决定精读](#deep-read)
- [保存报告](#save)
- [以后再加同类论文](#more-papers)
- [示例](#examples)
- [规则](#rules)
- [安装](#install)
  - [Claude Code](#claude-code)
  - [Codex CLI](#codex-cli)
  - [OpenCode](#opencode)
  - [依赖](#dependencies)
- [局限性](#limitations)
- [常见问题](#faq)
- [反馈与交流](#feedback)
- [点个 Star](#star)
- [License](#license)
- [声明](#disclaimer)

<a id="preview"></a>

## 🔍 先判断值不值得读

每篇先给一段预览，讲四件事：老问题是什么、它解决了什么、怎么解决的、结果如何。前三件各 **3–5 句**，要写清现有方法卡在哪、本文用了什么模块和机制；结果**至少给一个关键数字或对比对象**，不能用几个关键词糊弄。

这一轮只翻摘要、引言、相关工作、结论，不读全文。资料不够就标"仅摘要，未经正文核验"。

分区在收到论文时就查，不等写报告时补。理工医看 2025 中科院分区；中文人文社科看南核（CSSCI）和北核（北大核心）；英文人文看 SSCI/A&HCI；计算机会议看 CCF 第七版 A/B/C。查不到就写查不到，非计算机会议标 N/A。

预览之后你可以选：精读全文、只读方法、只读实验、收藏、暂不读。没有选择，它不会自己往下读。

如果选的是收藏或暂不读，就不问阅读目的，也不生成报告。

<p align="center"><img src="docs/images/flow-preview.png" width="680"></p>

<a id="deep-read"></a>

## 📖 决定精读

确认要读之后，再问阅读目的：精读、复现、找创新点、找选题、写综述。目的不同，报告详略不同。

<p align="center"><img src="docs/images/flow-choose.png" width="680"></p>

报告按 **14 节**写：

1. 基本信息：题目、作者、期刊、DOI、分区
2. 一句话结论
3. 摘要全文，加两个问题、两个做法
4. 整体框架与全流程，每步写做什么、为什么
5. 两到五个关键公式，附符号表
6. 创新点：老问题、创新做法、解决了什么
7. 实验：数据、设置、对比、消融
8. 结论全文，加作者自认的局限
9. Claim–Evidence 速查
10. 批判性审阅：效度问题、最强反驳、回避点、复现最可能失败的环节
11. 可复现性（文科为材料与引文）
12. 在相关工作里的位置
13. 对自己的启发和可行动项
14. 没解决的问题
附录：证据索引，记页码、章节、原文短引

摘要和结论放全文。英文摘要默认翻成中文，人名、机构、术语保留英文。

文科论文不写复现和代码，第 11 节改成材料与引文，第 10 节也不写"复现最可能失败环节"。

公式在中间稿里用 LaTeX，导出报告时转成图片，报告里看不到源码。

图从 PDF 抽到 `figures/`，放在对应段落后面，跟一句"画了什么、怎么看、说明什么"。抽不出来就说明，不硬凑。

只读方法或只读实验也可以，但会保留一道交叉检查：读方法看假设有没有被实验验证，读实验看实验有没有对上作者声称的贡献。

<a id="save"></a>

## 💾 保存报告

默认放在当前目录的 `papers/`，保存前会问一句要不要换位置。

保存前**先归类**，不会自己塞：

- 读 `_topics.md` 和 `_index.md`，给两三个候选主题，附上库里最接近的论文。
- 你选候选、新建主题、放进 `_inbox`，或者不保存。
- 只有一篇时直接存；两篇以上才问分开存、合并存、还是都要。
- 合并版会多一节跨篇比较，不写就只是把文件堆在一起。

目录长这样：

```
papers/
  _index.md
  _topics.md
  _inbox/
  <序号-中文主题>/
    _topic.md
    <年份-一作-中文短名>/
      report.docx
      figures/
```

文件夹用中文：主题写 `<序号>-<中文主题>`，论文写 `<年份>-<一作>-<中文短名>`。索引里仍用英文小写 `paper_id` 做唯一键。

每篇**只留一份 docx 报告**。**Markdown 只是转换用的中间文件**，导出成功后删除。报告里公式已经转成图片；版式是正文仿宋_GB2312 四号、标题二号、英文 Times New Roman、首行缩进 2 字符、表格文字居中，一句话结论和关键数字带黄色马克笔底色。

存完会报绝对路径、生成了哪些文件、索引改了什么。

<p align="center"><img src="docs/images/flow-save.png" width="680"></p>

<a id="more-papers"></a>

## ➕ 以后再加同类论文

直接发新论文就行，PDF、DOI、arXiv 都可以。流程还是预览、你选、精读、保存。

保存时它会先**读现有索引**：

- 按 DOI、arXiv ID、标题+年份+一作查重。
- 已有主题就给候选，让你决定加到现有主题还是新建。
- 同一篇二次精读（比如这次只看方法）会存成 v2，**不覆盖旧版**。
- 如果该主题下有合并版报告，会追加新篇并重新生成跨篇综述。
- 索引更新日期，旧报告保留。

所以一个主题可以慢慢攒：先放一两篇，后面遇到同类论文继续加，最后形成自己的小型文献库。

<a id="examples"></a>

## 🖼️ 示例

两篇跑完的报告。每篇 9 张缩略图，点开看大图；完整报告在下方链接里。

**英文论文**

*Mixed-attention variational autoencoding generative adversarial networks for rolling bearing fault diagnosis*

Measurement, 2026, 258, 119414  
DOI: 10.1016/j.measurement.2025.119414

<table>
<tr><td><a href="docs/images/meng/grid-01.png"><img src="docs/images/meng/grid-01.png" width="260"></a></td><td><a href="docs/images/meng/grid-02.png"><img src="docs/images/meng/grid-02.png" width="260"></a></td><td><a href="docs/images/meng/grid-03.png"><img src="docs/images/meng/grid-03.png" width="260"></a></td></tr>
<tr><td><a href="docs/images/meng/grid-04.png"><img src="docs/images/meng/grid-04.png" width="260"></a></td><td><a href="docs/images/meng/grid-05.png"><img src="docs/images/meng/grid-05.png" width="260"></a></td><td><a href="docs/images/meng/grid-06.png"><img src="docs/images/meng/grid-06.png" width="260"></a></td></tr>
<tr><td><a href="docs/images/meng/grid-07.png"><img src="docs/images/meng/grid-07.png" width="260"></a></td><td><a href="docs/images/meng/grid-08.png"><img src="docs/images/meng/grid-08.png" width="260"></a></td><td><a href="docs/images/meng/grid-09.png"><img src="docs/images/meng/grid-09.png" width="260"></a></td></tr>
</table>

完整报告：[报告](docs/examples/mixed-attention-vaegan.docx)

**中文论文**

沈从文创作的思想价值论——写在沈从文百年诞辰之际

《文学评论》2002 年第 6 期，第 5–17 页  
DOI：无

<table>
<tr><td><a href="docs/images/ling/grid-01.png"><img src="docs/images/ling/grid-01.png" width="260"></a></td><td><a href="docs/images/ling/grid-02.png"><img src="docs/images/ling/grid-02.png" width="260"></a></td><td><a href="docs/images/ling/grid-03.png"><img src="docs/images/ling/grid-03.png" width="260"></a></td></tr>
<tr><td><a href="docs/images/ling/grid-04.png"><img src="docs/images/ling/grid-04.png" width="260"></a></td><td><a href="docs/images/ling/grid-05.png"><img src="docs/images/ling/grid-05.png" width="260"></a></td><td><a href="docs/images/ling/grid-06.png"><img src="docs/images/ling/grid-06.png" width="260"></a></td></tr>
<tr><td><a href="docs/images/ling/grid-07.png"><img src="docs/images/ling/grid-07.png" width="260"></a></td><td><a href="docs/images/ling/grid-08.png"><img src="docs/images/ling/grid-08.png" width="260"></a></td><td><a href="docs/images/ling/grid-09.png"><img src="docs/images/ling/grid-09.png" width="260"></a></td></tr>
</table>

完整报告：[报告](docs/examples/shen-congwen.docx)

<a id="rules"></a>

## 📏 规则

- 用户没选，不开始精读。
- 摘要不能当全文结论用。
- 分区、页码、数字不能凭印象写。
- 保存后必须说路径、更新索引。
- 一次不超过 5 篇。

<a id="install"></a>

## ⚙️ 安装

<a id="claude-code"></a>

### Claude Code

直接把整个 `Easy-reading-papers` 文件夹放进：

```text
~/.claude/skills/Easy-reading-papers/
```

如果以后发布成 Claude Code 插件，可以用插件市场的方式装：

```bash
/plugin marketplace add <你的 GitHub 仓库>
/plugin install Easy-reading-papers@<市场名>
```

没有上架时，用上面的文件夹方式就行。

<a id="codex-cli"></a>

### Codex CLI

放到 Codex 的 skills 目录：

```text
~/.agents/skills/Easy-reading-papers/
```

<a id="opencode"></a>

### OpenCode

放到 OpenCode 的全局 skills 目录：

```text
~/.config/opencode/skills/Easy-reading-papers/
```

Windows 下通常是：

```text
C:\Users\<用户名>\.config\opencode\skills\Easy-reading-papers\
```

<a id="dependencies"></a>

### 依赖

```bash
pip install pymupdf python-docx matplotlib
```

装完重启对应工具，或重新打开一个会话。然后发一篇 PDF 或 DOI，问"这篇值不值得读？"就能试。

`papers/` 会建在当前工作目录。不装依赖也能做预览和精读，只是不能抽图、不能导出报告。

<a id="limitations"></a>

## ⚠️ 局限性

- **扫描版 PDF**：文件能打开，但整页是图片，没有文字层。摘要、公式、页码和图表文字都提取不到，只能标"没拿到正文"。需要先用 OCR（Acrobat、ABBYY、Tesseract 等）转成可搜索 PDF，或换出版社的文字版文件。
- **只有 DOI 时**：先用 Crossref 和出版社页面的题录、摘要做预览，这只代表能判断大致内容，不代表读了全文。要精读时再找开放获取全文；找不到会请你发 PDF，不绕过付费墙。只有摘要时会标"仅摘要，未经正文核验"，不写页码、图号和具体实验数字。
- **分区和收录**：每次联网查。理工医看 2025 中科院分区，中文人文看 CSSCI 和北大核心，英文人文看 SSCI/A&HCI，计算机会议看 CCF 第七版。没有网络、查不到、或 ISSN 对不上时，标"未收录"即可。
- **图里的信息**：纯文本模型只能读图注和正文，读不到图里的曲线、坐标和数值。涉及图内趋势时会明确标"未核验"，需要你自己看图或提供原始数据。
- **公式和表格**：PDF 解析失败时会标"公式/表格无法解析"，不凭印象补全。

<a id="faq"></a>

## ❓ 常见问题

**Q：我用的模型不能识图，还能用吗？**

能，但图里的内容会打折。文字、摘要翻译、裁图、排版、导出都正常；区别是混淆矩阵错在哪、曲线收不收敛、方法图哪块对应哪块，它只能靠正文和图注推测。遇到这种情况会明确说"图我看不到"，不编结论。要补图里的信息，换多模态模型，或把关键图单独发给识图模型问清楚。

**Q：我的方向没有数据集怎么办？**

文科、理论、综述类论文直接跳过数据集。第 5 节写关键命题，第 7 节写材料与论证，第 11 节写材料与引文，不写代码和复现。

**Q：只有 DOI 或者遇到付费墙怎么办？**

先用 Crossref 题录和摘要做预览，判断值不值得读。要精读再找开放获取全文；找不到会请你发 PDF，不绕过付费墙。只有摘要时会标"仅摘要，未经正文核验"。

**Q：扫描版 PDF 怎么办？**

先 OCR 成可搜索 PDF，或换出版社的文字版。没有文字层时只能标"没拿到正文"，不会硬写报告。

**Q：为什么保存后只有 docx，没有 Markdown？**

docx 是给人看的最终报告。Markdown 只是生成时的中间稿，导出成功后删除，避免两份内容不同步。

**Q：分区查不到怎么办？**

标"未收录"，不猜。中文刊写核心收录（CSSCI、北大核心等），不写"几区"。

**Q：以后找到同类论文，怎么加进已有主题？**

直接发新论文，保存时它会读索引、查重、给候选主题；加到现有主题或新建都可以。合并版会重新生成跨篇比较。

<a id="feedback"></a>

## 💬 反馈与交流

欢迎反馈意见，下面是微信：

<p align="center"><img src="docs/images/wechat-qr.jpg" width="220"></p>

<a id="star"></a>

## ⭐ 点个 Star

如果这个 skill 帮你省下了筛论文、精读、整理笔记的时间，点个 Star 就行。顺手转给同门也可以。

有新的领域写法或模板，欢迎 PR 回来。

<a id="license"></a>

## 📜 License

© 辽大TJ

<a id="disclaimer"></a>

## ⚠️ 声明

本 skill 只做论文阅读和报告生成的自动化，不替代你对论文的理解；报告由 AI 生成，结论需要自己核对。论文的图、表、原文版权归原作者与出版方所有，公开分享时请注意引用规范。医学、法律、工程等高风险场景不要只依据本报告，发现冲突时以原文为准。
