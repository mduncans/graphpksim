# PyPKSim

A simple simulation widget for a two-compartment pharmacokinetic (PK) model, exploring graph-theoretic representations of the system.

## Graph theoretic representation
The graph laplacian can be computed as the difference of the degree matrix and the adjacency matrix
$$
L \left( \mathcal{D} \right) = \Delta\left( \mathcal{D} \right) - A\left(\mathcal{D}\right)
$$
This matrix represents the flow through the system (out of each node). We can use this matrix to write the system of differential equations that describe the PK concentrations $c(t)$ with an initial dose of $D_0$:
$$
\dot{c}(t) = -L^T \left(\mathcal{D} \right) c(t) + D_0
$$