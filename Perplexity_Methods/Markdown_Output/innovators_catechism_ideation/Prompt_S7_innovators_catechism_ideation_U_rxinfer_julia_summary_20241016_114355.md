## Full Title of Project
### Innovators Catechism - RxInfer.jl: Reactive Message-Passing for Bayesian Inference

## Team Name
### Bayesian Intelligent Autonomous Systems (BIASlab)

## Facilitator(s)
### Dmitry Bagaev and the BIASlab Team

## Contact Information
### [BIASlab GitHub](https://github.com/biaslab) | [RxInfer.jl GitHub](https://github.com/ReactiveBayes/RxInfer.jl)

## Start Date
### 10-16-2024

## Situation
### Key Problems:
- The need for real-time Bayesian inference in complex probabilistic models, particularly in applications such as self-driving vehicles, extended reality, and signal processing.
- Limitations of sampling-based inference methods, which do not scale well to large models with many latent states.
- The inefficiency of manual and automated gradient methods for variational inference in real-time applications.

### User Segments:
- Researchers and developers in AI, machine learning, and probabilistic programming.
- Engineers in fields like robotics, autonomous systems, and cognitive science.
- Data scientists dealing with real-time data streams and large probabilistic models.

## Mission
### Value Proposition:
To provide a fast, efficient, and scalable framework for real-time Bayesian inference using reactive message passing on factor graphs, enabling accurate and continuous processing of infinite data streams and large static data sets.

## Potential Avenues of Approach
### Approach:
- Utilize reactive programming paradigms to handle asynchronous data streams.
- Employ factor graph representations of probabilistic models to facilitate efficient message passing.
- Support hybrid inference methods to optimize the trade-off between accuracy and computational speed.
- Integrate with other Julia packages for extended functionality and automatic differentiation.

## Key Features and Advantages of RxInfer.jl

### Theoretical Context
- **Variational Message Passing:** RxInfer.jl uses variational inference methods such as belief propagation, structured and mean-field variational message passing, expectation propagation, and conjugate-computation variational inference (CVI). These methods are optimized for real-time processing by leveraging statistical independencies and conjugate pairings of variables.
- **Factor Graphs:** The package represents probabilistic models as factor graphs, which are collections of nodes and edges capturing probabilistic relationships between variables. This representation allows for efficient and scalable inference.
- **Reactive Programming:** RxInfer.jl is built on a reactive programming framework, enabling the processing of infinite asynchronous data streams and continuous updating of the posterior distribution in real-time.

### Installation and Setup
To use RxInfer.jl, start by installing the package:
```julia
using Pkg
Pkg.add("RxInfer")
```

### Defining a Simple Bayesian Model
Here is an example of defining a linear state-space model using RxInfer.jl:

```julia
using RxInfer

@model function SSM(x0, y, A, B, Q, P)
    x_prior ~ MvNormal(x0, Q)
    x_prev = x_prior
    for i in eachindex(y)
        x[i] ~ MvNormal(A * x_prev, Q)
        y[i] ~ MvNormal(B * x[i], P)
        x_prev = x[i]
    end
end

# Load observations
observations = load_dataset()

# Perform inference
result = infer(
    model = SSM(x0 = prior_x, A = A, B = B, Q = Q, P = P),
    data = (y = observations,)
)
```

### Performing Inference
RxInfer.jl automates the inference process using reactive message passing. The `infer` function takes the model and data as inputs and returns the inference results. The process involves continuous updating of the posterior distribution as new data arrives.

### Advanced Features
- **Custom Factor Nodes:** Users can extend the built-in functionality by defining custom nodes and message update rules, making the package highly extensible.
- **Scheduling Strategies:** The package allows for customized trade-offs between accuracy and speed by specifying different inference methods at different locations in the graph.
- **Integration with Other Julia Packages:** RxInfer.jl supports integration with packages like ForwardDiff.jl and ReverseDiff.jl for automatic differentiation, enhancing parameter tuning and model optimization.

## Comparison with Other Probabilistic Programming Tools
- **Turing.jl and Stan.jl:** Unlike these packages, RxInfer.jl is specifically designed for real-time Bayesian inference on large probabilistic models. It outperforms generic-purpose Bayesian inference methods in terms of speed and accuracy, especially in models with conjugate likelihood-prior pairings.

## Potential Use Cases
- **Signal Processing:** Tracking hidden states of dynamic systems in real-time.
- **Robotics:** Smart navigation and collision avoidance.
- **Cognitive Science:** Reactive reasoning and decision-making using the Active Inference framework.

## Current Limitations, Ongoing Developments, and Future Directions
- **Current Limitations:** While highly efficient, the package may still face challenges with extremely complex models or very large datasets. Manual tuning of inference constraints can be necessary for optimal performance.
- **Ongoing Developments:** Continuous improvement of the inference engine, expansion of precomputed analytical inference solutions, and integration with more Julia packages.
- **Future Directions:** Expanding the scope of applications to more fields, such as finance and healthcare, and further optimizing the reactive programming framework for edge computing and IoT applications.

## Resources
- **Official Documentation:** [RxInfer.jl Documentation](https://rxinfer.ml)
- **Tutorials:** [Intro to RxInfer.jl by Doggo.jl](https://www.youtube.com/watch?v=_vVHWzK9NEI)
- **Academic Papers:** [RxInfer: A Julia package for reactive real-time Bayesian inference](https://www.theoj.org/joss-papers/joss.05161/10.21105.joss.05161.pdf)
- **GitHub Repository:** [ReactiveBayes/RxInfer.jl](https://github.com/ReactiveBayes/RxInfer.jl)
- **JuliaCon Presentations:** [RxInfer.jl: a package for real-time Bayesian Inference :: JuliaCon 2023](https://pretalx.com/juliacon2023/talk/WQNE9L/)