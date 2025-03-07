import spy_qqq
import optimizer
import excel_process
total_index, returns, alpha_beta_matrix, alpha, exp_ret, beta = await spy_qqq.concat_spy_qqq()
total_index, optimal_weights, cov, correlation=optimizer.run_optimizer(total_index.copy(), returns.copy())
excel_process.output_excel(optimal_weights, returns, total_index, correlation)
