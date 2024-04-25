import matplotlib.pyplot as plt
import numpy as np

rng = np.random.default_rng(seed=100)

## Create figure showcasing ADJUST/SetQ
## Create base vectors
baselvl = 100
t = np.linspace(-10, 10, 21)  ## Time
o = np.linspace(baselvl, baselvl, 21)  ## Observed
s = np.linspace(baselvl, baselvl, 21)  ## Simulated
rand_h = rng.dirichlet(np.ones(10), size=1)  ## Make random sample that adds up to 1
rand_h2 = rng.dirichlet(np.ones(10), size=1)  ## Make different random sample that adds up to 1
o[1:11] = baselvl + np.cumsum(rand_h * 1.5)  ## Scale increase by 1.5 for observations as bias
o[11:] = o[10] + np.cumsum(
    rand_h2 * 1.5
)  ## Scale increase by 1.5 for observations as bias, start from t = t0
s[1:11] = (
    baselvl + np.cumsum(rand_h) + rng.normal(0, 1, size=10) / 25
)  ## create simulation with small random error on top of bias
s[11:] = s[10] + np.cumsum(rand_h2) + rng.normal(0, 1, size=10) / 25  ## start from t = t0

offset_t0 = o[10] - s[10]  ## Define error at t0
bias_rate = (o[10] - baselvl) / (s[10] - baselvl)
s_set_q = s[10:] + offset_t0  ## Set sim to obs at t0
## sim increase from t0 onwards multiplied by avg error rate from t-10 to t0, starting from obs t0
s_adjust = (s[10:] - s[10]) * bias_rate + o[
    10
]  ## Set sim to obs at t=0, scale sim after t_o with average error rate

plt.figure(figsize=(10, 6))
plt.scatter(t[:11], o[:11], c="k", label="observed", zorder=2)
plt.plot(
    t[11:],
    o[11:],
    c="k",
    label="observed, future",
    zorder=2,
    marker="o",
    markerfacecolor="none",
    linestyle="",
)
plt.plot(t, s, c="b", linestyle=":", label="simulated")
plt.plot(t[10:], s_set_q, c="b", linestyle="--", label="simulated, fix at t0")
plt.plot(t[10:], s_adjust, c="b", linestyle="-", label="simulated, error extrapolation past t0")
plt.vlines(x=0, color="k", linestyle="--", ymin=baselvl, ymax=baselvl + 3)
plt.xlabel("Time [hh:mm]")
xlabs = []
xticks = [-9, -6, -3, 0, 3, 6, 9]
[xlabs.append(f"{str((12 + x)%24).zfill(2)}:00") for x in xticks]
plt.xticks(xticks, xlabs)
plt.ylabel("h [m]")
plt.text(x=-0.4, y=(baselvl + 3.05), s="now")
plt.legend()


## Plot fig for SetQ documentation
## Q_obs_y, Q_sim_y, Q_sim_t, Q_sim_set_q
t = np.linspace(0, 24, 25)
Q_obs_y = np.linspace(400, 405, 25) + rng.normal(0, 5, size=25)
Q_sim_y = Q_obs_y - 3 + rng.normal(0, 4, size=25)
Q_sim_t = Q_sim_y - 1 + rng.normal(0, 5, size=25)
Q_obs_y[12:16] = Q_obs_y[12:16] + 40

Q_sim_set_q = Q_sim_t + 2 - 2
Q_sim_set_q[12:16] = Q_obs_y[12:16]


plt.figure(figsize=(10, 6))
plt.scatter(t, Q_obs_y, c="grey", label="observed yesterday", zorder=4)
plt.plot(t, Q_sim_y, c="blue", label="simulated yesterday", alpha=0.5, linestyle=":")
plt.plot(t, Q_sim_t, c="blue", label="simulated today", linestyle="--")
plt.plot(t, Q_sim_set_q, c="blue", label="simulated today, set_q", linestyle="-")
plt.legend()
plt.xlabel("Time [hh:mm]")
xlabs = []
xticks = [0, 3, 6, 9, 12, 15, 18, 21, 24]
[xlabs.append(f"{str(x%24).zfill(2)}:00") for x in xticks]
plt.xticks(xticks, xlabs)
plt.ylabel("Q_out [m3/s]")


## Set_q nan_options
t = np.linspace(0, 24, 25)
Q_obs_y = np.array(
    [
        10,
        10,
        10,
        200,
        200,
        100,
        100,
        10,
        10,
        10,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        100,
        100,
        100,
        300,
        300,
        300,
        200,
        200,
        200,
        10,
        10,
    ]
)
Q_sim = Q_obs_y[:] + 2 - 2
t1, t2 = 10, 100
Q_setq_prev = [10] * 5 + [100]
Q_setq_next = [10] + [100] * 5
Q_setq_closest = [10, 10, 10, 100, 100, 100]
Q_setq_interp = np.linspace(10, 100, 6)

plt.figure(figsize=(10, 6))
plt.plot(t, Q_sim, c="blue", label="simulated", alpha=0.5, linestyle=":")
plt.plot(t[9:15], Q_setq_prev, c="red", label="simulated, set_q_prev", linestyle="--", marker="o")
plt.plot(t[9:15], Q_setq_next, c="green", label="simulated, set_q_next", linestyle="-.", marker="o")
plt.plot(
    t[9:15],
    Q_setq_closest,
    c="purple",
    label="simulated, set_q_closest",
    linestyle="-.",
    marker="o",
)
plt.plot(
    t[9:15], Q_setq_interp, c="orange", label="simulated, set_q_interp", linestyle="-.", marker="o"
)
plt.scatter(
    t, Q_obs_y, c="k", label="observed yesterday", zorder=2
)  ## zorder to force observation on top of plot
plt.legend()
plt.title("Solving data gaps with set_q")
plt.xlabel("Time [hh:mm]")
xlabs = []
xticks = [0, 3, 6, 9, 12, 15, 18, 21, 24]
[xlabs.append(f"{str(x%24).zfill(2)}:00") for x in xticks]
plt.xticks(xticks, xlabs)
plt.ylabel("Q_out [m3/s]")

## Adjust blend-param
t = np.linspace(0, 24, 25)
obs = np.linspace(100, 103, 25)
sim = obs - 2
base_zeros = [0] * 12
cor05 = []
cor02 = []
cor2_0 = []
cor5_0 = []
sim2 = np.array(sim[12])
sim5 = np.array(sim[12])
sim2_0 = np.array(sim[12])
sim5_0 = np.array(sim[12])
for x in range(13):
    ob = obs[12 + x]
    ob_0 = obs[12]
    trend = 3 / 24
    dsim2 = ob - (sim2 + trend)
    dsim5 = ob - (sim5 + trend)
    sim2 = (sim2 + trend) + dsim2 * 0.2
    sim5 = (sim5 + trend) + dsim5 * 0.5
    cor02.append(sim2)
    cor05.append(sim5)

    dsim2_0 = ob_0 - sim2_0
    dsim5_0 = ob_0 - sim5_0
    sim2_0 = sim2_0 + dsim2_0 * 0.2
    sim5_0 = sim5_0 + dsim5_0 * 0.5
    cor2_0.append(sim2_0)
    cor5_0.append(sim5_0)


plt.scatter(t[:13], obs[:13], color="k", label="observations")
plt.scatter(t[13:], obs[13:], color="grey", label="latest obs + trend")
plt.scatter(t[13:], [obs[12]] * 12, color="grey", label="latest obs", marker="x")
plt.plot(t[12:], cor02, linestyle="dashed", label="blend factor 0.2, trend")
plt.plot(t[12:], cor05, linestyle="dashed", label="blend factor 0.5, trend")
plt.plot(t[12:], cor2_0, linestyle="dashed", label="blend factor 0.2, latest obs", marker="x")
plt.plot(t[12:], cor5_0, linestyle="dashed", label="blend factor 0.5, latest obs", marker="x")
plt.plot(t, sim, label="sim original")
plt.vlines(x=12, ymin=97, ymax=103, color="k", linestyle=":")
plt.legend()
plt.xlabel("t [hh:mm]")
xlabs = []
xticks = [0, 3, 6, 9, 12, 15, 18, 21, 24]
[xlabs.append(f"{str(x%24).zfill(2)}:00") for x in xticks]
plt.xticks(xticks, xlabs)

plt.ylabel("h [m]")
plt.text(x=11.6, y=(103.05), s="now")
