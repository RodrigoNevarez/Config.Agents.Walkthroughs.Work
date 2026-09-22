# **The Epistemology of Propositional Titling: Structural, Cognitive, and Architectural Foundations in Knowledge Management**

In technical documentation, cognitive engineering, and personal knowledge management, the syntax chosen to title an artifact dictates how that artifact is synthesized, retrieved, and combined into broader networks of thought1. The conventional practice of labeling documents with broad categorical nouns—such as titling a note "Python"—creates passive, indeterminate containers2. In contrast, titling documents with complete declarative assertions—such as "Python source compiles to intermediate bytecode prior to virtual machine interpretation"—converts static text into modular, falsifiable units of thought1.  
This titling paradigm traces a continuous conceptual trajectory from mid-century sociocybernetics through classical hypertext theory to contemporary cognitive science1. Moving beyond categorical indexing to claim-based architecture fundamentally alters the cognitive ergonomics of knowledge capture, minimizes retrieval friction, and equips knowledge systems to operate as computational extensions of human reasoning1.

## **The Transition from Categorical Labels to Propositional Architecture**

Categorical titling reflects traditional library taxonomy, where information is divided into hierarchical containers defined by broad subject matter2. In personal and technical documentation, this convention prompts authors to create all-inclusive files dedicated to broad tools or domains2. A file titled "Python" inevitably accumulates disconnected observations regarding grammar syntax, the Global Interpreter Lock, dynamic typing semantics, standard libraries, and runtime benchmarks2.  
Because such topic-based files house disparate concepts, they place substantial demands on human working memory during subsequent review2. A researcher returning to a categorical document must visually scan the entire text to locate a specific operational mechanism, evaluate the internal logical coherence of conflicting paragraphs, and manually determine which aspects of the note remain relevant to their active work2. Furthermore, categorical notes fail to provide meaningful semantic links; connecting a passage to \[\[Python\]\] communicates nothing about the underlying causality, constraints, or assertions being referenced1.  
The migration toward modular, assertion-level documentation emerged from Niklas Luhmann’s analog *Zettelkasten* methodology1. While Luhmann relied on an alphanumeric branching index to maintain dynamic positional relationships without rigid thematic silos, his foundational criterion was the intellectual autonomy of the card: every note had to express a coherent argument comprehensible entirely on its own1. Sönke Ahrens systematized this approach by isolating the principle of "atomicity," asserting that long-term intellectual momentum requires knowledge to accrete around atomic ideas rather than temporal sources or generic topics3.  
Andy Matuschak formalized the linguistic requirements of this philosophy through the framework of "Evergreen Notes"4. Matuschak established that digital knowledge work must prioritize concept-oriented factoring over project- or author-based filing2. To enforce this conceptual separation, Matuschak introduced the operational rule: *Prefer note titles with complete phrases to sharpen claims*4. Phrasing a document title as a full sentence with an explicit predicate forces the author to state what is mechanically or empirically asserted, shifting documentation from passive data storage to active intellectual sensemaking4.

## **Cognitive Mechanisms and Epistemic Affordances**

Transforming document titles from nominal categories into declarative claims engages specific cognitive operations that fundamentally change how information is processed, retained, and retrieved.

### **Epistemic Pressure as an Analytical Diagnostic**

Categorical titling conceals incomplete comprehension4. An author can readily file ambiguous, contradictory, or superficial notes under "Python" because a broad noun phrase imposes no criteria for logical cohesion2. By contrast, attempting to formulate a single declarative sentence imposes severe epistemic pressure4. If an author experiences friction while attempting to state a sharp thesis within the title boundary, that difficulty acts as an immediate diagnostic indicator that the thought is either conceptually muddy or conflating multiple distinct mechanisms4.  
For example, attempting to title a file *"Python is an interpreted language with significant runtime costs due to dynamic type resolution and the Global Interpreter Lock"* immediately exposes structural overextension. The syntactic awkwardness signals that three independent propositions have been artificially merged: runtime bytecode interpretation, the performance overhead of dynamic attribute lookups, and single-threaded CPU concurrency constraints. Compelling the title to state a single claim forces the author to factor complex domains into their atomic mechanics, isolating distinct dependencies before linking them together1.

### **Cognitive Load and Structural Scaffolding**

The cognitive advantages of declarative titling during information retrieval find rigorous validation in Michael Alley’s *Assertion-Evidence Framework*13. Originally developed to replace bullet-point slide presentations in technical and engineering disciplines, Alley's framework replaces topical headers with succinct, sentence-length assertions supported directly by visual and empirical evidence14.  
Controlled studies evaluating technical presentations demonstrate that participants exposed to assertion-evidence designs experience lower perceived extraneous cognitive load, while demonstrating statistically superior immediate comprehension and long-term recall of complex concepts compared to cohorts exposed to conventional topic-subtopic headings5. Topic titles impose heavy working-memory demands because the audience must actively parse complex text while deducing the overarching point16. A declarative headline provides an immediate top-down cognitive schema; the supporting narrative is instantly parsed through the lens of that explicit thesis16. In digital knowledge repositories, scanning a directory of propositionally titled documents provides direct schema comprehension at every node, whereas scanning a list of topical nouns requires diving into each document's body to extract its functional premise8.

### **Combinatorial Synthesis and Modular Linkage**

Knowledge generation relies on combinatorial synthesis, wherein existing concepts are reorganized and connected across domains to reveal novel properties2. Categorical documents resist modular linkage because their conceptual boundaries are fluid and ill-defined2. Linking "Python" to "Compiler Design" establishes a low-signal associative relationship that fails to specify the underlying computational dynamics.  
Conversely, proposition-titled documents operate as formal logical premises capable of direct assembly into broader arguments1. An author constructing a manuscript, engineering specification, or analytical evaluation can sequence proposition notes directly within expository prose1. Because each linked title encapsulates a verified, atomic assertion, the title serves as an active grammatical and logical component of the higher-level thesis1. Knowledge accretion ceases to be an act of manual transcription and becomes an act of weaving pre-factored, falsifiable assertions into new conceptual tapestries1.

## **Architectural Refinements: Titles as Application Programming Interfaces**

The concept of the proposition-titled document achieves architectural utility when viewed through software abstraction principles. Matuschak posits that well-factored evergreen note titles function directly like Application Programming Interfaces (APIs)1.

| API Design Principle | Propositional Titling Analogue | Operational Impact on Knowledge Work |
| :---- | :---- | :---- |
| **Separation of Concerns** | Single-claim atomicity1 | Restricts the note to a single assertion, eliminating conceptual cross-contamination1. |
| **Information Hiding / Abstraction** | Complete claim encapsulation1 | The title serves as an intellectual handle, allowing downstream work to reference the idea without re-evaluating its internals1. |
| **Interface Contracts** | Rigorous declarative phrasing1 | Establishes unambiguous conceptual boundaries that prevent semantic drift across linked networks1. |
| **Subtree Abstraction** | Nested modular hierarchies1 | Allows higher-level synthesis notes to combine lower-level claim handles into sophisticated intellectual frameworks1. |

When a document is titled with an exact proposition, the title forms an intellectual contract1. The body of the document provides the underlying implementation—the citations, empirical datasets, methodological boundaries, and code snippets12. As the knowledge repository matures, the author constructs higher-level conceptual notes that link together existing assertion handles, creating layered abstraction models that mirror modular software architectures1.  
A vital operational refinement within this API model is Matuschak’s insistence on positive title framing24. Inexperienced authors frequently frame claims as negative critiques, such as "Dynamic typing is harmful for enterprise codebases"24. Negatively framed titles foreground an operational failure without articulating the underlying structural dynamic24. Refactoring such statements into positive assertions—such as "Static typing eliminates runtime type-coercion bugs in distributed architectures"—exposes the causal theory, systematically anchoring the claim within observable engineering principles24.

## **Semantic Discourse Graphs: Decoupling Claim from Evidence**

A critical limitation of basic evergreen note-taking is the conflation of empirical observations with synthetic claims inside a single document container12. To address this structural flaw, information science research led by Joel Chan developed the *Discourse Graph* framework8. Drawing from argument visualization and scholarly communication theory, the Discourse Graph architecture deconstructs complex inquiry into an explicit semantic schema containing Question, Claim, and Evidence (QCE) nodes12.  
Within this formal architecture, inquiry begins with Question nodes, which capture open research questions or systemic problems without forcing a premature conclusion12. These questions branch into multiple Claim nodes, which are titled with atomic, present-tense declarative assertions representing synthetic answers or theoretical interpretations12. Crucially, Claim nodes do not house raw experimental data12. Instead, they link bidirectionally to discrete Evidence nodes12.  
Evidence nodes capture empirical observations grounded strictly in context, methodology, and past-tense phrasing12. By isolating observations from interpretations, the Discourse Graph prevents the corruption of historical findings when theories evolve12. Multiple opposing claims can link to the identical evidence node, preserving academic rigor and transparent disagreement without breaking the coherence of the documentation network12.

## **Systemic Friction, Pathologies, and Technical Limitations**

Despite the epistemic benefits of proposition-based titling, dogmatic adherence to declarative sentences across an entire documentation infrastructure generates acute operational pathologies.

### **Premature Formalization and Cognitive Resistance**

Hypertext pioneers Catherine C. Marshall and Frank M. Shipman III documented that human sensemaking degrades when systems demand *premature structuring* or *premature formalization*6. In the nascent stages of learning or research, an individual's conceptual grasp of a domain is non-linear, fragmented, and unstable6.  
Requiring an author to crystallize an incomplete inkling into a polished declarative claim title before saving the file introduces high cognitive resistance7. When tools coerce users into rigid schemas before understanding has emerged, users experience operational dread, frequently abandoning the system28. Fluid, unstructured staging environments—such as fleeting scratchpads or temporary capture journals—are structurally required to incubate ideas prior to formal declarative titling7.

### **Semantic Brittleness and the Identity Coupling Problem**

In many contemporary digital knowledge tools, the file name, document title, and linking identifier are unified into a single text string33. Systems analysis on *zettelkasten.de* highlights that using full propositional statements as unique identifiers creates severe semantic friction34. Authors find themselves forced to contort sentences inside host documents so that a verbose, proposition-titled target note integrates naturally into the grammar of a linked sentence9.  
Furthermore, as understanding deepens, an author inevitably refines the nuance of a claim34. Changing a title to reflect this evolution risks semantic dissonance across historical documents that linked to the original, unqualified claim34. For this reason, rigorous knowledge architectures decouple the immutable identity of the file (using arbitrary numeric or UUID strings) from the volatile descriptive assertion contained within the document's primary heading33.

### **The Nuance Fallacy in Technical Disciplines**

The user's query example—*"Python is an interpreted programming language"*—demonstrates how declarative titling can introduce technical inaccuracy if applied naively. In computer systems engineering, categorizing a language as "interpreted" represents a category error that confuses a language specification with a specific runtime implementation.  
Python itself is an abstract grammar specification detailing syntax and semantics. The standard implementation, CPython, compiles source code into intermediate bytecode instructions that are executed by a stack-based virtual evaluation loop. Alternative implementations, such as PyPy, employ tracing Just-In-Time (JIT) compilation to emit native machine instructions dynamically, while implementations like Jython or IronPython compile Python source to JVM bytecode or Common Intermediate Language. Freezing the simplistic claim *"Python is an interpreted programming language"* into a document title ossifies an inaccurate premise into the knowledge base, where its declarative authority discourages deeper analysis of compiler-interpreter boundaries.

## **Methodological Comparison Across Knowledge Frameworks**

Different knowledge engineering frameworks resolve the trade-offs between rapid capture, structural rigidity, and synthetic rigor in distinct ways.

| Knowledge Framework | Primary Titling Paradigm | Architectural Mechanism | Cognitive Load Distribution | Optimal Domain Application |
| :---- | :---- | :---- | :---- | :---- |
| **Evergreen Notes** (Andy Matuschak)1 | Propositional / Declarative Sentences4 | Atomic claim abstraction handles; dense concept linking1 | High upfront synthesis cost; minimal downstream composition friction2 | Monographic writing, academic research, philosophy1 |
| **Assertion-Evidence** (Michael Alley)13 | Assertion Headlines (![][image1] lines)15 | Presentation slide pairing an assertion with empirical visuals15 | Eliminates split-attention effect; optimizes audience memory encoding5 | Engineering briefings, technical lecturing, scientific defense14 |
| **Discourse Graphs** (Joel Chan et al.)23 | Semantic Prefixes: ![][image2], ![][image3], ![][image4] \[cite: 12, 23\] | Fine-grained graphs separating raw observations from synthetic claims8 | Moderate encoding load; maximum evidentiary auditability12 | Collaborative research, clinical meta-analyses, team science23 |
| **Building a Second Brain** (Tiago Forte)36 | Clean Nouns or Source Titles37 | Actionability-oriented folders; layered progressive summarization36 | Low initial capture friction; opportunistic distillation during project work19 | Professional workflows, corporate knowledge, project delivery36 |
| **Maps of Content** (Nick Milo)9 | Hybrid: Claims for notes; Topical hubs for MOCs9 | Bottom-up emergent collation moving from atomic notes to structural hubs9 | Low early-stage friction; reflective consolidation at scale thresholds20 | Broad conceptual exploration, curriculum mastery, creative ideation9 |
| **Classical Zettelkasten** (Niklas Luhmann)10 | Alphanumeric Index IDs (Folgezettel)1 | Branching physical slip-box sequences linked by arbitrary adjacency1 | Zero upfront titling friction; high index maintenance and search load10 | Cross-disciplinary sociology, lifelong scholarship, analog archives10 |

## **Practical Implementation: The Polymorphic Titling Taxonomy**

The solution to the document titling challenge is not the dogmatic enforcement of declarative sentences across all files, but the adoption of a polymorphic titling taxonomy. Because a knowledge system processes fundamentally different types of intellectual objects, it must apply distinct grammatical conventions based on an artifact’s epistemic function.

### **Tier 1: Entity and Definition Artifacts**

Entity files establish baseline terminology, canonical definitions, concrete specifications, libraries, or physical entities4. These documents are not arguments; they describe mechanisms or formal rules without advocating an interpretive position4. They use strict noun phrases for titles, such as CPython Virtual Machine Execution Architecture or Global Interpreter Lock Specification4.

### **Tier 2: Propositional and Claim Artifacts**

Claim files represent the synthetic analytical core of the knowledge system4. They make a single, falsifiable assertion regarding a mechanism, trade-off, or observed behavior, supported internally by evidence and framed in positive language4. They use complete, active declarative sentences, such as CPython virtual machine bytecode evaluation incurs runtime overhead via monolithic switch-dispatch loops or NumPy vectorized operations bypass Python interpreter overhead via contiguous C memory buffers4.

### **Tier 3: Inquiry and Research Artifacts**

When a practitioner confronts an unsolved problem or nascent inquiry, coercing an immediate assertion causes premature formalization4. Inquiry artifacts capture open research vectors while providing clear investigative focus, with the explicit systemic mandate that they be refactored into Tier 2 claims once resolved4. They use focused question syntax, such as To what extent does Python 3.12's specialized adaptive interpreter reduce runtime dynamic dispatch? or Under what memory access patterns does dynamic typing degrade L1 cache efficiency?4.

### **Tier 4: Structural Index Artifacts**

Structural documents serve as navigation consoles, aggregating lower-tier claims into linear arguments, pedagogical roadmaps, or project outlines4. They avoid lengthy sentences, opting for designated prefix symbols combined with thematic scope, such as § CPython Runtime Optimization Strategies or MOC \- High-Throughput Python Infrastructure4.

### **Cross-Domain Refactoring Models**

Applying this polymorphic taxonomy transforms weak, ambiguous topical containers into precise, modular architectural assets across diverse professional disciplines.

| Discipline | Topical Container Title | Intermediate Broad Claim | Refined Polymorphic Architecture |
| :---- | :---- | :---- | :---- |
| **Software Systems** | Python | Python is an interpreted programming language | **Entity:** CPython Execution Architecture **Claim:** CPython compiles source to bytecode before virtual machine evaluation **Claim:** Dynamic typing degrades runtime throughput via redundant pointer indirection **Inquiry:** How does tracing JIT compilation mitigate CPython dispatch latency? |
| **Cognitive Science** | Memory | Spaced repetition improves memory | **Entity:** Ebbinghaus Forgetting Curve **Claim:** Expanding retrieval intervals optimize long-term synaptic memory consolidation **Claim:** Context-independent flashcard recall degrades situational application fluency **Inquiry:** What interval latency maximizes retention during complex technical skill acquisition? |
| **Distributed Systems** | Microservices | Microservices are better than monoliths | **Entity:** Remote Procedure Call Protocol **Claim:** Microservice boundaries incur distributed transaction overhead across data stores **Claim:** Asynchronous event buses decouple service deployability at the cost of eventual consistency **Inquiry:** At what organizational team scale does microservice overhead become net positive? |
| **Molecular Biology** | CRISPR | CRISPR cures genetic diseases | **Entity:** CRISPR-Cas9 Endonuclease Mechanism **Claim:** Cas9 non-homologous end joining introduces random insertion-deletion mutations **Claim:** Base editing eliminates double-stranded breaks by leveraging deaminase fusions **Inquiry:** What molecular modifications minimize off-target Cas9 cleavage in eukaryotic cells? |

## **Conclusion**

The assertion that "document titling matters" reflects the cognitive physics of externalized human thought. Titling a document "Python" relegates a knowledge base to a passive filing cabinet, demanding significant cognitive re-parsing upon every subsequent interaction2. Refactoring that title to "Python is an interpreted programming language" marks a significant evolution toward propositional synthesis, converting an inert label into a falsifiable assertion capable of modular linkage1.  
The definitive refinement of this practice, however, requires recognizing that a declarative sentence is an intellectual API contract that must be factored to atomic boundaries, technically verified, and integrated into a broader polymorphic taxonomy1. By reserving noun phrases for canonical entities, using interrogatives to guide active inquiry, and deploying precise, positively framed declarative sentences for analytical claims, knowledge workers build repositories that operate not merely as administrative archives, but as active computational partners in intellectual discovery1.

#### **Works cited**

> 1. Evergreen note titles are like APIs, [https://notes.andymatuschak.org/zDh1yhNFQNxDEre12B4zd8k](https://notes.andymatuschak.org/zDh1yhNFQNxDEre12B4zd8k)  
> 2. Evergreen notes should be concept-oriented, [https://notes.andymatuschak.org/z2hQEhqWkdRLL9JUwfawZZx?ref=josephnoelwalker.com](https://notes.andymatuschak.org/z2hQEhqWkdRLL9JUwfawZZx?ref=josephnoelwalker.com)  
> 3. Evergreen notes should be concept-oriented | annotated by tyler, [https://readwise.io/reader/shared/01hhmbgq7w3d5w1fgzty3q1c0g/](https://readwise.io/reader/shared/01hhmbgq7w3d5w1fgzty3q1c0g/)  
> 4. Prefer note titles with complete phrases to sharpen claims, [https://notes.andymatuschak.org/zLhoRUyjKU665EY16u4XXJy](https://notes.andymatuschak.org/zLhoRUyjKU665EY16u4XXJy)  
> 5. Developing, designing, and delivering more effective research and, [https://pmc.ncbi.nlm.nih.gov/articles/PMC13432626/](https://pmc.ncbi.nlm.nih.gov/articles/PMC13432626/)  
> 6. Frank M. Shipman III and Catherine C. Marshall, [https://spl.cde.state.co.us/artemis/ucbserials/ucb51110internet/1993/ucb51110648internet.pdf](https://spl.cde.state.co.us/artemis/ucbserials/ucb51110internet/1993/ucb51110648internet.pdf)  
> 7. Evergreen notes, [https://notes.andymatuschak.org/z5E5QawiXCMbtNtupvxeoEX](https://notes.andymatuschak.org/z5E5QawiXCMbtNtupvxeoEX)  
> 8. Discourse graphs could significantly accelerate human synthesis work, [https://scalingsynthesis.com/c-discourse-graphs-could-significantly-accelerate-human-synthesis-work/](https://scalingsynthesis.com/c-discourse-graphs-could-significantly-accelerate-human-synthesis-work/)  
> 9. AIP 59 Generate Novel Insights With This 3-Step Linked Book, [https://medium.com/@aidan.helfant/aip-59-generate-novel-insights-with-this-3-step-linked-book-notetaking-process-e78874bb053a](https://medium.com/@aidan.helfant/aip-59-generate-novel-insights-with-this-3-step-linked-book-notetaking-process-e78874bb053a)  
> 10. 10 Principles to Revolutionize Your Note-Taking and Writing, [https://fortelabs.com/blog/how-to-take-smart-notes/](https://fortelabs.com/blog/how-to-take-smart-notes/)  
> 11. Sönke Ahrens' How to Take Smart Notes: Modern Systematization of, [https://www.ernestchiang.com/en/posts/2025/sonke-ahrens-how-to-take-smart-notes/](https://www.ernestchiang.com/en/posts/2025/sonke-ahrens-how-to-take-smart-notes/)  
> 12. PTN \- discourse graph \- Joel Chan's working notes \- Obsidian Publish, [https://publish.obsidian.md/joelchan-notes/discourse-graph/patterns/PTN+-+discourse+graph](https://publish.obsidian.md/joelchan-notes/discourse-graph/patterns/PTN+-+discourse+graph)  
> 13. 5.12 Designing Assertion-Evidence Slide Decks \- FHSU Digital Press, [https://fhsu.pressbooks.pub/strategicbcomm/chapter/5-12-message-strategy-evidence/](https://fhsu.pressbooks.pub/strategicbcomm/chapter/5-12-message-strategy-evidence/)  
> 14. The Craft of Scientific Presentations summary \- Blinkist, [https://www.blinkist.com/books/the-craft-of-scientific-presentations-en](https://www.blinkist.com/books/the-craft-of-scientific-presentations-en)  
> 15. Template for Assertion-Evidence slide. The ... \- ResearchGate, [https://www.researchgate.net/figure/Template-for-Assertion-Evidence-slide-The-assertion-evidence-slide-structure-encourages\_fig8\_274552916](https://www.researchgate.net/figure/Template-for-Assertion-Evidence-slide-The-assertion-evidence-slide-structure-encourages_fig8_274552916)  
> 16. How the design of presentation slides affects audience, [https://pure.psu.edu/en/publications/how-the-design-of-presentation-slides-affects-audience-comprehens/](https://pure.psu.edu/en/publications/how-the-design-of-presentation-slides-affects-audience-comprehens/)  
> 17. Assertion-Evidence Slides Appear to Lead to Better Comprehension, [https://www.researchgate.net/publication/344533171\_Assertion-Evidence\_Slides\_Appear\_to\_Lead\_to\_Better\_Comprehension\_and\_Recall\_of\_More\_Complex\_Concepts](https://www.researchgate.net/publication/344533171_Assertion-Evidence_Slides_Appear_to_Lead_to_Better_Comprehension_and_Recall_of_More_Complex_Concepts)  
> 18. The Rule of Seven: Optimal Slide Content for Maximum Retention, [https://twistly.ai/the-rule-of-seven-optimal-slide-content-for-maximum-retention/](https://twistly.ai/the-rule-of-seven-optimal-slide-content-for-maximum-retention/)  
> 19. Progressive Summarization VI: Core Principles of Knowledge Capture, [https://every.to/forte-labs/progressive-summarization-vi-core-1534225](https://every.to/forte-labs/progressive-summarization-vi-core-1534225)  
> 20. 5 Simple Levels To Supercharging Your Learning With MOCs In, [https://www.aidanhelfant.com/5-simple-levels-to-supercharging-your-learning-with-mocs-in-obsidian/](https://www.aidanhelfant.com/5-simple-levels-to-supercharging-your-learning-with-mocs-in-obsidian/)  
> 21. Evergreen note titles are like APIs, [https://notes.andymatuschak.org/zNUaiGAXp21eorsER1Jm9yU?stackedNotes=z3XP5GRmd9z1D2qCE7pxUvbeSVeQuMiqz9x1C](https://notes.andymatuschak.org/zNUaiGAXp21eorsER1Jm9yU?stackedNotes=z3XP5GRmd9z1D2qCE7pxUvbeSVeQuMiqz9x1C)  
> 22. 𝍌 Evergreen note titles are like APIs \- Joel Gascoigne, [https://joel.is/notes/Evergreen\_note\_titles\_are\_like\_APIs/](https://joel.is/notes/Evergreen_note_titles_are_like_APIs/)  
> 23. Discourse Graphs and the Future of Science | Protocol Labs Research, [https://research.protocol.ai/blog/2023/discourse-graphs-and-the-future-of-science/](https://research.protocol.ai/blog/2023/discourse-graphs-and-the-future-of-science/)  
> 24. Prefer positive note titles to promote systematic theory, [https://notes.andymatuschak.org/z63PA5ATVi8oyhyLgeGvL3p](https://notes.andymatuschak.org/z63PA5ATVi8oyhyLgeGvL3p)  
> 25. Discourse Graphs | A Tool for Collaborative Knowledge Synthesis, [https://discoursegraphs.com/](https://discoursegraphs.com/)  
> 26. Discourse Graph Plugin \- RemNote, [https://feedback.remnote.com/p/discourse-graph-plugin](https://feedback.remnote.com/p/discourse-graph-plugin)  
> 27. Discovering Implicit Structure in Spatial Hypertext, [https://people.engr.tamu.edu/shipman/viki/papers/ht93/ht93.html](https://people.engr.tamu.edu/shipman/viki/papers/ht93/ht93.html)  
> 28. (PDF) Facilitated hypertext for collective sensemaking \- ResearchGate, [https://www.researchgate.net/publication/228986737\_Facilitated\_hypertext\_for\_collective\_sensemaking\_15\_years\_on\_from\_gIBIS](https://www.researchgate.net/publication/228986737_Facilitated_hypertext_for_collective_sensemaking_15_years_on_from_gIBIS)  
> 29. Argument diagramming and planning cognition in argumentative, [https://etheses.bham.ac.uk/5048/2/Chryssafidou14PhD.pdf](https://etheses.bham.ac.uk/5048/2/Chryssafidou14PhD.pdf)  
> 30. Questions-Claim-Evidence/Discourse Graph in Obsidian?, [https://forum.obsidian.md/t/questions-claim-evidence-discourse-graph-in-obsidian/48685](https://forum.obsidian.md/t/questions-claim-evidence-discourse-graph-in-obsidian/48685)  
> 31. Progressive Summarization \- Fork My Brain, [https://notes.nicolevanderhoeven.com/sources/Course/Progressive+Summarization](https://notes.nicolevanderhoeven.com/sources/Course/Progressive+Summarization)  
> 32. How to Take Smart Notes \- Sönke Ahrens \- Taniyn Quest, [https://publish.obsidian.md/taniynquest/03+The+Library/Books/How+to+Take+Smart+Notes+-+S%C3%B6nke+Ahrens](https://publish.obsidian.md/taniynquest/03+The+Library/Books/How+to+Take+Smart+Notes+-+S%C3%B6nke+Ahrens)  
> 33. Title in the body of the note...why? \- Zettelkasten Forum, [https://forum.zettelkasten.de/discussion/2055/title-in-the-body-of-the-note-why](https://forum.zettelkasten.de/discussion/2055/title-in-the-body-of-the-note-why)  
> 34. [https://zettelkasten.de/posts/the-hidden-problem-with-note-titles-as-links-and-how-to-fix-it/](https://zettelkasten.de/posts/the-hidden-problem-with-note-titles-as-links-and-how-to-fix-it/)  
> 35. ID Zettel only title, not number \- Zettelkasten Forum, [https://forum.zettelkasten.de/discussion/564/id-zettel-only-title-not-number](https://forum.zettelkasten.de/discussion/564/id-zettel-only-title-not-number)  
> 36. The PARA Method \- Book Review \- RK's Musings, [https://www.rksmusings.com/2025/03/19/para-method-book-review/](https://www.rksmusings.com/2025/03/19/para-method-book-review/)  
> 37. How to Build a Personal Knowledge Management System \- Atlas, [https://www.atlasworkspace.ai/blog/personal-knowledge-management-system](https://www.atlasworkspace.ai/blog/personal-knowledge-management-system)  
> 38. Depths of Obsidian \- Null Patch, [https://nullpat.ch/posts/2024/08/depths-of-obsidian/](https://nullpat.ch/posts/2024/08/depths-of-obsidian/)  
> 39. Progressive Summarization A Practical Technique for Designing, [https://garden.synesthesia.co.uk/references/readwise/articles/progressive-summarization-a-practical-technique-for-designing-discoverable-notes-forte-2017/](https://garden.synesthesia.co.uk/references/readwise/articles/progressive-summarization-a-practical-technique-for-designing-discoverable-notes-forte-2017/)  
> 40. Progressive Summarization: A Practical Technique for Designing, [https://fortelabs.com/blog/progressive-summarization-a-practical-technique-for-designing-discoverable-notes/](https://fortelabs.com/blog/progressive-summarization-a-practical-technique-for-designing-discoverable-notes/)  
> 41. Is Progressive Summarization a Waste of Time? \- James Stuber, [https://jamesstuber.com/progressive-summarization-a-waste/](https://jamesstuber.com/progressive-summarization-a-waste/)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAVCAYAAABVAo5cAAAAd0lEQVR4XmNgGAWjYBRQABiBWAuIo4GYGYppAliB2BeItwNxMhBzo0pTD4AMzmeAWOTNQCMfSQJxNxSvAWI9BkhQUh2oA/FiBohFIEtBmKZAmYHOFsIAcpCCHABKlTQJUmyALokGG6BbtoABulsIA3QraUYBSQAALfUPjXA2XdMAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAZCAYAAAABmx/yAAABJklEQVR4XuXTvytGURzH8a9kEJGIRSkbg4WEDEaLv8AzGJSSUhL5AywGySh/gcFmU5gUi4FMBqVMksEo3p9zvqfOk3ufnm42n3oN55z7PfeeH9fs/6Ydq7jGBZ7cAbqy5+oygjuso9X72twRztHt/SFD7hFLaMkHPcN4xVrq0AyaSU4szl6UTlziLHXU8OXmU2dBUqGEVCpMjVvX4w8VpQ8PFpcUdvENx65RxvGJw7yx7RpFu6nlzKnRTGGvu7Fs19N37zplFPsYs3ieW05nrLMO0cAO7t0UNtGBDSzjxU14TUjlQkWXWp8mHxYv8yKucIpBp7tbdqtsAAsWd24Ps9nYNGaydml0rs8W3yq//oyyrOAb726yfrg8WlO/xWspTady4d/nB2i6Q9VfyGcNAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAZCAYAAAABmx/yAAAA60lEQVR4XmNgGLmAFYgjgPgKEL8C4kdQ3A7EfEDchFCKAGpAfA6I1wGxIpqcNxDfBuKDyILyUHwdiCuBmBlZEgpYgHgNEM+BCfAD8R4oPgDEPDAJLGASEEfDOBlA/BeKPWCCOEAfEBvDOGRpBDnrABBfhWIRhBr8QBOI3wLxUihmRJXGDUDWfgXiKijGB0CukYBx9IH4ExCXQzE+kAjEljCOIBCfBuL5UIzNqQpQXMcASVVwAArVd1BshizBAHHadCgGJRAUQLZGkPU1UPwNiGcxQBJ5PxAvYIBohgcKLgBKfm5QLIwmNwpoCgDSVC7+hACafQAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAZCAYAAAABmx/yAAABAElEQVR4Xu3QL2uCURQG8DNcUNQwgzIcCGoZCH4Dk0nQMGwyWFsXBMPCYIhFBA0GyzDY9gUWxegHMG8sOSw2w5zPee8j758pQ5OgD/zgvefcc7n3FTmtBKgO/X90OGPFR1F4gSUU4NohATX45owrFzCECVx5eho/9LxFjW7WoVcxh2jiFIEgtFh3JQsLeORah58oCZeQZ8+VgwcrsIJnKEMT3ilkb/ubLnzAg5jBAWtqa8I0hjcxV9IU4Y40Kcjx28otzaHqqKfF/E2l79VextGXEv3IjseLOaQt9m2sNOgLbpwNrtVIzOGu7D14L2azXnFD1580g1+aQsyMnXNEWQMmmDVp3wjjrwAAAABJRU5ErkJggg==>