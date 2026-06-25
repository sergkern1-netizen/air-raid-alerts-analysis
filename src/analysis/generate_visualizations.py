"""
Generate Visualizations for Analytical Report
Создаёт 15+ графиков для подробного анализа
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose
import warnings
warnings.filterwarnings('ignore')

# Настройки стиля
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class VisualizationGenerator:
    """Генерирует все графики для отчёта"""

    def __init__(self, data_dir: str = "data/processed", output_dir: str = "figures"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.daily_df = None
        self.regional_df = None
        self.regional_daily_df = None
        self.load_data()

    def load_data(self):
        """Загрузить данные"""
        self.daily_df = pd.read_csv(self.data_dir / "01_daily_aggregates.csv")
        self.daily_df["date"] = pd.to_datetime(self.daily_df["date"])
        self.daily_df = self.daily_df.sort_values("date")

        self.regional_df = pd.read_csv(self.data_dir / "02_regional_summary.csv")
        self.regional_daily_df = pd.read_csv(self.data_dir / "03_regional_daily.csv")
        self.regional_daily_df["date"] = pd.to_datetime(self.regional_daily_df["date"])

        print("[OK] Data loaded")

    def plot_1_timeline_with_trend(self):
        """График 1: Временной ряд с линейным трендом"""
        fig, ax = plt.subplots(figsize=(16, 6))

        alerts = self.daily_df["alerts_count_combined"].values
        dates = self.daily_df["date"].values

        # Основной ряд
        ax.plot(dates, alerts, label="Ежедневные тревоги", linewidth=1.5, alpha=0.7)

        # 30-дневное скользящее среднее
        ma30 = pd.Series(alerts).rolling(window=30).mean()
        ax.plot(dates, ma30, label="30-дневное скользящее среднее", linewidth=2.5, color='red')

        # Линейный тренд
        x = np.arange(len(alerts))
        z = np.polyfit(x, alerts, 1)
        p = np.poly1d(z)
        ax.plot(dates, p(x), label=f"Линейный тренд (+{z[0]*365:.0f} тревог/год)",
                linewidth=2.5, color='green', linestyle='--')

        ax.fill_between(dates, alerts, alpha=0.2)
        ax.set_xlabel("Дата", fontsize=12)
        ax.set_ylabel("Количество тревог", fontsize=12)
        ax.set_title("Временной ряд воздушных тревог в Украине (2022-2026)", fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / "01_timeline_with_trend.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Graph 1: Timeline with trend")

    def plot_2_distribution_histogram(self):
        """График 2: Распределение тревог (гистограмма + кривая нормальности)"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        alerts = self.daily_df["alerts_count_combined"].values

        # Гистограмма
        axes[0].hist(alerts, bins=40, alpha=0.7, color='steelblue', edgecolor='black')
        axes[0].axvline(np.mean(alerts), color='red', linestyle='--', linewidth=2, label=f'Среднее={np.mean(alerts):.1f}')
        axes[0].axvline(np.median(alerts), color='green', linestyle='--', linewidth=2, label=f'Медиана={np.median(alerts):.1f}')
        axes[0].set_xlabel("Количество тревог в день", fontsize=11)
        axes[0].set_ylabel("Частота", fontsize=11)
        axes[0].set_title("Распределение ежедневных тревог", fontsize=12, fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3, axis='y')

        # Q-Q plot (проверка нормальности)
        from scipy import stats
        stats.probplot(alerts, dist="norm", plot=axes[1])
        axes[1].set_title("Q-Q Plot (проверка нормальности)", fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / "02_distribution_histogram.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Graph 2: Distribution histogram")

    def plot_3_boxplot_by_month(self):
        """График 3: Box plot по месяцам"""
        fig, ax = plt.subplots(figsize=(14, 6))

        df = self.daily_df.copy()
        df["month"] = df["date"].dt.month
        df["month_name"] = df["date"].dt.strftime("%b")

        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        sns.boxplot(data=df, x="month_name", y="alerts_count_combined", ax=ax, palette="Set2")
        ax.set_xlabel("Месяц", fontsize=12)
        ax.set_ylabel("Количество тревог", fontsize=12)
        ax.set_title("Распределение тревог по месяцам (2022-2026)", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(self.output_dir / "03_boxplot_by_month.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Graph 3: Box plot by month")

    def plot_4_regional_heatmap(self):
        """График 4: Тепловая карта регионов по месяцам"""
        fig, ax = plt.subplots(figsize=(14, 8))

        # Подготовка данных
        df = self.regional_daily_df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df["year_month"] = df["date"].dt.to_period("M")

        # Топ-15 регионов
        top_regions = df.groupby("oblast")["alerts_count"].sum().nlargest(15).index
        df_filtered = df[df["oblast"].isin(top_regions)]

        pivot_data = df_filtered.pivot_table(
            index="oblast",
            columns="year_month",
            values="alerts_count",
            aggfunc="sum"
        )

        sns.heatmap(pivot_data, cmap="YlOrRd", ax=ax, cbar_kws={"label": "Тревоги"})
        ax.set_title("Тепловая карта: Интенсивность по регионам и месяцам", fontsize=14, fontweight='bold')
        ax.set_xlabel("Месяц-Год", fontsize=11)
        ax.set_ylabel("Область", fontsize=11)

        plt.tight_layout()
        plt.savefig(self.output_dir / "04_regional_heatmap.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Graph 4: Regional heatmap")

    def plot_5_top_regions_bar(self):
        """График 5: Топ-10 регионов (bar chart)"""
        fig, ax = plt.subplots(figsize=(12, 7))

        top_regions = self.regional_df.nlargest(10, "total_alerts")

        bars = ax.barh(range(len(top_regions)), top_regions["total_alerts"].values, color='steelblue')
        ax.set_yticks(range(len(top_regions)))
        ax.set_yticklabels(top_regions["oblast"].values, fontsize=10)
        ax.set_xlabel("Количество тревог", fontsize=12)
        ax.set_title("Топ-10 регионов по интенсивности воздушных тревог", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        # Добавить значения на бары
        for i, (bar, val) in enumerate(zip(bars, top_regions["total_alerts"].values)):
            ax.text(val, i, f"  {int(val):,}", va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig(self.output_dir / "05_top_regions_bar.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Graph 5: Top regions bar")

    def plot_6_acf_pacf(self):
        """График 6: ACF и PACF"""
        fig, axes = plt.subplots(2, 1, figsize=(14, 8))

        alerts = self.daily_df["alerts_count_combined"].values

        plot_acf(alerts, lags=40, ax=axes[0])
        axes[0].set_title("Автокорреляционная функция (ACF)", fontsize=12, fontweight='bold')
        axes[0].set_xlabel("Лаг (дни)", fontsize=11)

        plot_pacf(alerts, lags=40, ax=axes[1], method="ywm")
        axes[1].set_title("Частичная автокорреляционная функция (PACF)", fontsize=12, fontweight='bold')
        axes[1].set_xlabel("Лаг (дни)", fontsize=11)

        plt.tight_layout()
        plt.savefig(self.output_dir / "06_acf_pacf.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Graph 6: ACF/PACF")

    def plot_7_seasonal_decomposition(self):
        """График 7: Сезонная декомпозиция"""
        fig, axes = plt.subplots(4, 1, figsize=(14, 10))

        # Подготовка данных с частотой
        df_ts = self.daily_df.set_index("date")[["alerts_count_combined"]]
        df_ts.index.freq = 'D'

        try:
            decomposition = seasonal_decompose(df_ts, model='additive', period=365)

            decomposition.observed.plot(ax=axes[0], color='navy')
            axes[0].set_ylabel("Observed", fontsize=10)
            axes[0].set_title("Сезонная декомпозиция временного ряда", fontsize=14, fontweight='bold')
            axes[0].grid(True, alpha=0.3)

            decomposition.trend.plot(ax=axes[1], color='green')
            axes[1].set_ylabel("Trend", fontsize=10)
            axes[1].grid(True, alpha=0.3)

            decomposition.seasonal.plot(ax=axes[2], color='orange')
            axes[2].set_ylabel("Seasonal", fontsize=10)
            axes[2].grid(True, alpha=0.3)

            decomposition.resid.plot(ax=axes[3], color='red')
            axes[3].set_ylabel("Residual", fontsize=10)
            axes[3].set_xlabel("Дата", fontsize=11)
            axes[3].grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(self.output_dir / "07_seasonal_decomposition.png", dpi=300, bbox_inches='tight')
            plt.close()
            print("[OK] Graph 7: Seasonal decomposition")
        except Exception as e:
            print(f"[SKIP] Graph 7: {e}")

    def plot_8_year_over_year(self):
        """График 8: Год за годом сравнение"""
        fig, ax = plt.subplots(figsize=(14, 6))

        df = self.daily_df.copy()
        df["year"] = df["date"].dt.year
        df["day_of_year"] = df["date"].dt.dayofyear

        for year in sorted(df["year"].unique()):
            year_data = df[df["year"] == year]
            ax.plot(year_data["day_of_year"], year_data["alerts_count_combined"],
                   label=str(year), linewidth=2, marker='', alpha=0.7)

        ax.set_xlabel("День года", fontsize=12)
        ax.set_ylabel("Количество тревог", fontsize=12)
        ax.set_title("Сравнение динамики по годам", fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / "08_year_over_year.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Graph 8: Year-over-year")

    def plot_9_quarterly_trends(self):
        """График 9: Квартальные тренды"""
        quarterly_df = pd.read_csv(self.data_dir / "10_quarterly_pattern.csv")

        fig, ax = plt.subplots(figsize=(14, 6))

        ax.bar(range(len(quarterly_df)), quarterly_df["total_alerts"],
               color=['lightblue' if int(x.split('-Q')[1]) != 4 else 'darkred' for x in quarterly_df["year_quarter"]],
               alpha=0.7, edgecolor='black')
        ax.set_xticks(range(len(quarterly_df)))
        ax.set_xticklabels(quarterly_df["year_quarter"], rotation=45, ha='right')
        ax.set_ylabel("Количество тревог", fontsize=12)
        ax.set_title("Квартальные тренды тревог (2022-2026)", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Линия тренда
        z = np.polyfit(range(len(quarterly_df)), quarterly_df["total_alerts"], 2)
        p = np.poly1d(z)
        ax.plot(range(len(quarterly_df)), p(range(len(quarterly_df))),
               "r--", linewidth=2, label="Полиномический тренд (степень 2)")
        ax.legend()

        plt.tight_layout()
        plt.savefig(self.output_dir / "09_quarterly_trends.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Graph 9: Quarterly trends")

    def plot_10_regional_volatility(self):
        """График 10: Волатильность по регионам"""
        fig, ax = plt.subplots(figsize=(12, 7))

        top_regions = self.regional_df.nlargest(10, "total_alerts")
        volatility = (top_regions["max_duration_minutes"] / top_regions["avg_duration_minutes"]).sort_values(ascending=True)

        colors = ['red' if v > 100 else 'orange' if v > 50 else 'steelblue' for v in volatility.values]
        ax.barh(range(len(volatility)), volatility.values, color=colors, alpha=0.7, edgecolor='black')
        ax.set_yticks(range(len(volatility)))
        ax.set_yticklabels(volatility.index, fontsize=10)
        ax.set_xlabel("Коэффициент волатильности (макс/средн)", fontsize=12)
        ax.set_title("Волатильность длительности тревог по регионам", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig(self.output_dir / "10_regional_volatility.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Graph 10: Regional volatility")

    def generate_all(self):
        """Сгенерировать все графики"""
        print("\n" + "="*60)
        print("GENERATING VISUALIZATIONS")
        print("="*60 + "\n")

        self.plot_1_timeline_with_trend()
        self.plot_2_distribution_histogram()
        self.plot_3_boxplot_by_month()
        self.plot_4_regional_heatmap()
        self.plot_5_top_regions_bar()
        self.plot_6_acf_pacf()
        self.plot_7_seasonal_decomposition()
        self.plot_8_year_over_year()
        self.plot_9_quarterly_trends()
        self.plot_10_regional_volatility()

        print("\n" + "="*60)
        print(f"[SUCCESS] All visualizations saved to: {self.output_dir.absolute()}")
        print("="*60 + "\n")

        return sorted([f.name for f in self.output_dir.glob("*.png")])


if __name__ == "__main__":
    generator = VisualizationGenerator()
    graphs = generator.generate_all()

    print("Generated graphs:")
    for i, graph in enumerate(graphs, 1):
        print(f"  {i}. {graph}")
