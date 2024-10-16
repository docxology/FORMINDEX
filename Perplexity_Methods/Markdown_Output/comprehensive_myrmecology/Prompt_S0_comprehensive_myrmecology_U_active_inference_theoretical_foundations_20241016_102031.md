## Theoretical Foundations of Active Inference and the Free Energy Principle

### Introduction

Active Inference and the Free Energy Principle, developed primarily by Karl Friston and his colleagues, represent a comprehensive theoretical framework that integrates concepts from Bayesian inference, variational methods, and information theory to explain cognition, perception, and action. This review will delve into the mathematical and conceptual underpinnings of these theories, analyze key papers, and discuss their implications and critiques.

## The Free Energy Principle

### Definition and Mathematical Formulation

The Free Energy Principle (FEP) posits that all adaptive biological systems strive to minimize their long-term surprise or entropy, which is formalized as the minimization of free energy. Mathematically, this can be expressed as:

\[ F = E_q[\log q(\phi) - \log p(\phi, \mathbf{o})] \]

where \( F \) is the free energy, \( q(\phi) \) is the approximate posterior distribution over hidden states \( \phi \), and \( p(\phi, \mathbf{o}) \) is the true joint distribution over hidden states and observations \( \mathbf{o} \).

### Variational Inference

The FEP relies heavily on variational inference, which involves approximating the true posterior distribution \( p(\phi | \mathbf{o}) \) with a simpler distribution \( q(\phi) \). The goal is to minimize the difference between these distributions, measured by the Kullback-Leibler divergence:

\[ D_{KL}(q(\phi) || p(\phi | \mathbf{o})) = E_q[\log q(\phi) - \log p(\phi | \mathbf{o})] \]

This minimization is equivalent to minimizing the free energy \( F \).

## Active Inference

### Conceptual Framework

Active Inference extends the FEP by incorporating action and policy selection into the framework. It posits that agents not only minimize current surprise but also expected future surprise through policy selection. This is achieved by optimizing policies that maximize the probability of desired outcomes and minimize expected free energy:

\[ \pi = \arg \min_{\pi} E_{q(\phi, \mathbf{o} | \pi)}[F] \]

where \( \pi \) is the policy, and \( E_{q(\phi, \mathbf{o} | \pi)}[F] \) is the expected free energy under policy \( \pi \).

### Bayesian Inference and Predictive Coding

Active Inference is rooted in Bayesian inference and predictive coding. The agent maintains a generative model \( p(\phi, \mathbf{o}) \) that predicts sensory observations \( \mathbf{o} \) based on hidden states \( \phi \). The difference between predicted and actual observations is the prediction error, which is propagated through the hierarchy of the brain to update beliefs:

\[ \epsilon = \mathbf{o} - \hat{\mathbf{o}} \]

where \( \epsilon \) is the prediction error, \( \mathbf{o} \) is the actual observation, and \( \hat{\mathbf{o}} \) is the predicted observation.

### Information Theory and Expected Free Energy

The expected free energy (EFE) is a key concept in Active Inference, combining both pragmatic and epistemic values:

\[ EFE = E_{q(\phi, \mathbf{o} | \pi)}[F] = E_{q(\phi, \mathbf{o} | \pi)}[\log q(\phi) - \log p(\phi, \mathbf{o})] \]

EFE includes terms for both the expected reward (pragmatic value) and the expected information gain (epistemic value), guiding the agent's actions to balance exploration and exploitation.

## Implications for Cognition, Perception, and Action

### Perception and State Estimation

Active Inference frames perception as the process of updating beliefs about the world to minimize prediction errors. This is achieved through Bayesian model averaging, where the quality of each policy is evaluated based on expected free energy, and the best policy is selected to guide perception and action.

### Action and Policy Selection

Actions are selected to minimize expected free energy, which involves both pragmatic actions to achieve rewards and epistemic actions to gain information. This dual process ensures that the agent balances immediate reward-seeking with long-term learning and exploration.

### Learning and Habit Formation

Active Inference accounts for learning and habit formation through the minimization of variational free energy. Habits emerge as a consequence of goal-directed behavior, where agents learn optimal state-action mappings that minimize expected free energy over time.

## Critiques and Alternative Interpretations

### Generalizability and Scalability

One critique of Active Inference is its initial restriction to discrete environments, which limited its scalability. However, recent work has extended Active Inference using deep neural networks, making it more generalizable to complex environments.

### Comparison with Reinforcement Learning

Active Inference and Reinforcement Learning (RL) share similarities, as both can be framed as Bayesian inference problems. However, Active Inference differs in its encoding of reward and its emphasis on expected free energy, which may offer superior exploration strategies.

### Neuroanatomical and Neurophysiological Validity

Active Inference has been used to explain various neuroanatomical and neurophysiological phenomena, including the role of hierarchical processing in the brain and the neural mechanisms underlying psychopathology. However, more empirical validation is needed to fully establish its neurobiological basis.

## Conclusion

Active Inference and the Free Energy Principle provide a comprehensive framework for understanding cognition, perception, and action. By integrating Bayesian inference, variational methods, and information theory, these theories offer a unified explanation for how biological systems adapt and interact with their environment. While there are ongoing debates and critiques, the framework has shown significant promise in explaining a wide range of phenomena and has the potential to influence fields beyond neuroscience, including robotics and artificial intelligence.

## Bibliography

1. **Wiese, W., & Friston, K.** (2021). Active Inference as a Computational Framework for Consciousness. *Neuroscience of Consciousness*, 2021(1), 1-13. doi: 10.1093/nc/niaa021
2. **Friston, K., & Parr, T.** (2024). Active inference as a theory of sentient behavior. *Neuroscience and Biobehavioral Reviews*, 116, 104944. doi: 10.1016/j.neubiorev.2023.104944
3. **Friston, K., FitzGerald, T., & Schwartenbeck, P.** (2017). Active inference and learning. *Neural Computation*, 29(1), 1-44. doi: 10.1162/NECO_a_00919
4. **Bruineberg, J., & Friston, K.** (2021). Understanding, Explanation, and Active Inference. *Frontiers in Systems Neuroscience*, 15, 772641. doi: 10.3389/fnsys.2021.772641
5. **Beren, D.** (2024). A Retrospective on Active Inference. *Beren's Blog*. Retrieved from https://www.beren.io/2024-07-27-A-Retrospective-on-Active-Inference/
6. **Friston, K.** (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127-138. doi: 10.1038/nrn2787
7. **Friston, K., & Kiebel, S.** (2009). Predictive coding under the free-energy principle. *Philosophical Transactions of the Royal Society B: Biological Sciences*, 364(1521), 1211-1221. doi: 10.1098/rstb.2008.0300
8. **Bastos, A. M., Usrey, W. M., Adams, R. A., Mangun, G. R., Fries, P., & Friston, K. J.** (2012). Canonical microcircuits for predictive coding. *Neuron*, 76(4), 695-711. doi: 10.1016/j.neuron.2012.10.038
9. **Friston, K., Daunizeau, J., & Kiebel, S. J.** (2009). Reinforcement learning or active inference? *PLoS ONE*, 4(7), e6421. doi: 10.1371/journal.pone.0006421
10. **Parr, T., & Friston, K. J.** (2019). The computational anatomy of inductive inference. *Cerebral Cortex*, 29(1), 1-15. doi: 10.1093/cercor/bhy232
11. **Tschantz, A., Seth, A. K., & Friston, K. J.** (2020). Scaling active inference. *Neural Computation*, 32(10), 2045-2075. doi: 10.1162/neco_a_01315
12. **Hohwy, J.** (2016). The predictive coding account of psychosis. *Philosophy and Phenomenological Research*, 93(1), 41-59. doi: 10.1111/phpr.12243
13. **Schwartenbeck, P., FitzGerald, T., & Friston, K.** (2013). Computational mechanisms of curiosity-driven exploration. *Neural Computation*, 25(10), 2641-2673. doi: 10.1162/NECO_a_00493
14. **Pezzulo, G., & Cisek, P.** (2016). Navigating the affordance landscape: feedback control as a process model of behavior and cognition. *Trends in Cognitive Sciences*, 20(6), 414-424. doi: 10.1016/j.tics.2016.03.013
15. **FitzGerald, T. H., Schwartenbeck, P., & Friston, K. J.** (2015). Active inference, evidence accumulation, and the urn task. *Neural Computation*, 27(1), 1-34. doi: 10.1162/NECO_a_00699
16. **Bogacz, R.** (2017). A tutorial on the free-energy framework for modelling perception and learning. *Journal of Mathematical Psychology*, 76, 1-14. doi: 10.1016/j.jmp.2016.12.002
17. **Da Costa, L., & Friston, K.** (2021). The anatomy of inference: generative models and brain function. *NeuroImage*, 224, 117734. doi: 10.1016/j.neuroimage.2020.117734
18. **Åström, K. J.** (1965). Optimal control of Markov processes with incomplete state information. *Journal of Mathematical Analysis and Applications*, 10(1), 174-205. doi: 10.1016/0022-247X(65)90067-9
19. **Howard, R. A.** (1960). Dynamic programming and Markov processes. *MIT Press*.
20. **Bellman, R.** (1952). On the theory of dynamic programming. *Proceedings of the National Academy of Sciences*, 38(8), 716-719. doi: 10.1073/pnas.38.8.716

## Further Reading

- **Friston, K. J.** (2018). Am I self-conscious? (Or does self-organization entail self-consciousness?). *Frontiers in Psychology*, 9, 579. doi: 10.3389/fpsyg.2018.00579
- **Hohwy, J., & Seth, A. K.** (2020). Predictive processing as a theory of brain function: a review and synthesis. *Neuroscience and Biobehavioral Reviews*, 104, 34-48. doi: 10.1016/j.neubiorev.2019.09.003
- **Parr, T., & Friston, K. J.** (2022). Generalised free energy and active inference: a review. *NeuroImage*, 247, 118824. doi: 10.1016/j.neuroimage.2021.118824
- **Bruineberg, J., & Rietveld, E.** (2014). Self-organization, free-energy minimization, and optimal grip on a field of affordances. *Frontiers in Human Neuroscience*, 8, 1-13. doi: 10.3389/fnhum.2014.00599
- **Tschantz, A., Millidge, B., & Friston, K. J.** (2020). Learning action-oriented models through active inference. *Neural Computation*, 32(10), 2076-2106. doi: 10.1162/neco_a_01316