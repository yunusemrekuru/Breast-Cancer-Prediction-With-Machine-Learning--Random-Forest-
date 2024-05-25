import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, roc_curve, auc
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
import seaborn as sns

class MemeKanseriSiniflandirici:
    def __init__(self, veri_yolu="breast_cancer.csv", test_boyutu=0.2, rastgele_durum=42):
        try:
            self.veri = pd.read_csv(veri_yolu)
        except FileNotFoundError:
            raise FileNotFoundError(f"Veri dosyası bulunamadı: {veri_yolu}")

        self.veri.rename(columns={'Class': 'class'}, inplace=True)
        self.veri.dropna(inplace=True)
        self.veri.columns = self.veri.columns.str.strip()

        X = self.veri.drop("class", axis=1)
        y = self.veri["class"].replace({2: "iyi huylu", 4: "kötü huylu"})

        self.X_egitim, self.X_test, self.y_egitim, self.y_test = train_test_split(
            X, y, test_size=test_boyutu, random_state=rastgele_durum
        )

        self.model = RandomForestClassifier(n_estimators=100, random_state=rastgele_durum)

    def train(self):
        self.model.fit(self.X_egitim, self.y_egitim)

    def tahmin_et(self, X):
        return self.model.predict(X)

    def olasilik_tahmin_et(self, X):
        return self.model.predict_proba(X)[:, 1]

    def degerlendir(self):
        y_tahmin = self.tahmin_et(self.X_test)
        y_olasilik = self.olasilik_tahmin_et(self.X_test)

        dogruluk = accuracy_score(self.y_test, y_tahmin)
        kesinlik = precision_score(self.y_test, y_tahmin, pos_label="kötü huylu")
        duyarlilik = recall_score(self.y_test, y_tahmin, pos_label="kötü huylu")
        f1 = f1_score(self.y_test, y_tahmin, pos_label="kötü huylu")
        karmasiklik_matrisi = confusion_matrix(self.y_test, y_tahmin)
        rapor = classification_report(self.y_test, y_tahmin)

        print("Accuracy (Doğruluk):", dogruluk)
        print("F1 Score (F1 Puanı):", f1)
        print("\nPrecision (Hassasiyet):", kesinlik)
        print("Recall (Geri Çağırma):", duyarlilik)
        print("\nClassification Report:\n", rapor)

        # Karışıklık Matrisi Görselleştirme (Seaborn ile)
        plt.figure(figsize=(8, 6))
        sns.heatmap(karmasiklik_matrisi, annot=True, fmt="d", cmap="Blues",
                    xticklabels=self.model.classes_, yticklabels=self.model.classes_)
        plt.xlabel("Tahmin Edilen Sınıf")
        plt.ylabel("Gerçek Sınıf")
        plt.title("Karışıklık Matrisi")
        plt.show()

        # ROC Eğrisi Hesaplama
        fpr, tpr, thresholds = roc_curve(self.y_test, y_olasilik, pos_label="kötü huylu")
        roc_auc = auc(fpr, tpr)

        # ROC Eğrisi (Matplotlib ile)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC eğrisi (alan = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Yanlış Pozitif Oranı')
        plt.ylabel('Doğru Pozitif Oranı')
        plt.title('ROC Eğrisi')
        plt.legend(loc="lower right")
        plt.show()

        # Karar Ağacı Görselleştirme (Matplotlib ile)
        plt.figure(figsize=(20, 15))
        agac = self.model.estimators_[0]
        plot_tree(agac, feature_names=self.X_egitim.columns, class_names=self.model.classes_,
                  filled=True, rounded=True, fontsize=12, max_depth=2)
        plt.title("Karar Ağacı", fontsize=14)
        plt.show()

        # Özellik Önem Düzeyleri Grafiği
        onem = pd.Series(self.model.feature_importances_, index=self.X_egitim.columns)
        onem_sirali = onem.sort_values(ascending=False)

        plt.figure(figsize=(10, 8))
        sns.barplot(x=onem_sirali, y=onem_sirali.index)
        plt.xlabel('Önem Düzeyi')
        plt.ylabel('Özellik')
        plt.title("Random Forest Özellik Önem Düzeyleri")
        plt.xticks(rotation=45)
        plt.show()

if __name__ == "__main__":
    siniflandirici = MemeKanseriSiniflandirici("breast_cancer.csv")
    siniflandirici.train()
    siniflandirici.degerlendir()
