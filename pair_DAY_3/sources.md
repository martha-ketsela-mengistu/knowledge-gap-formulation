# Sources — Day 3

**Primary sources:**

1. Rafailov, R., Sharma, A., Mitchell, E., Manning, C. D., Ermon, S., & Finn, C. (2023). *Direct Preference Optimization: Your Language Model is Secretly a Reward Model.* NeurIPS 2023.  
   — DPO loss derivation and beta's role: Section 3. The closed-form optimal policy derivation (Section 3.1) is where beta survives from the RLHF objective into the DPO loss.

2. Stiennon, N., Ouyang, L., Wu, J., Ziegler, D. M., Lowe, R., Voss, C., Radford, A., Amodei, D., & Christiano, P. (2020). *Learning to Summarize with Human Feedback.* NeurIPS 2020.  
   — The KL-penalised RLHF objective that beta originates from: Section 3.1. Establishes the `max E[r] − β·KL(π ‖ π_ref)` formulation.

**Tool / experiment:**

- TRL `DPOTrainer` with GPT-2 on toy preference data, run at β = 0.01, 0.1, 0.5. Code in `pair_DAY_3/minimal_trl.ipynb`. Outputs: `beta_margins.png`, `beta_gradient_scale.png`.

