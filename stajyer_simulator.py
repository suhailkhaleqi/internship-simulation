"""
Stajyer Yerleştirme Simülatörü
Greedy ve Heuristic algoritmaları ile öğrenci-firma eşleştirmesi
"""

import csv
import random
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
from copy import deepcopy

# ==================== VERİ YAPILARI ====================

class Student:
    def __init__(self, student_id, preferences, gno):
        self.id = student_id
        self.preferences = preferences  # 5 firma tercihi listesi
        self.gno = gno
        self.assigned_firm = None
        self.is_placed = False

class Firm:
    def __init__(self, firm_id, capacity):
        self.id = firm_id
        self.capacity = capacity
        self.current_capacity = capacity
        self.assigned_students = []

# ==================== CSV OKUMA ====================

def load_students(filepath="students.csv"):
    """students.csv dosyasını oku"""
    students = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prefs = row['preferences'].split(',')
            student = Student(
                student_id=row['student_id'],
                preferences=prefs,
                gno=float(row['gno'])
            ) 
            students.append(student)
    return students

def load_firms(filepath="firms.csv"):
    """firms.csv dosyasını oku"""
    firms = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            firm_id = row['firma_id'].strip()
            firm = Firm(
                firm_id=firm_id,
                capacity=int(row['kapasite'])
            )
            firms[firm_id] = firm
    return firms

# ==================== YARDIMCI FONKSİYONLAR ====================

def reset_data(students, firms):
    """Verileri başlangıç durumuna sıfırla"""
    for s in students:
        s.assigned_firm = None
        s.is_placed = False
    for f in firms.values():
        f.current_capacity = f.capacity
        f.assigned_students = []

def get_unplaced_students(students):
    """Yerleşmemiş öğrencileri döndür"""
    return [s for s in students if not s.is_placed]

def get_available_firms(firms):
    """Boş kontenjanı olan firmaları döndür"""
    return {fid: f for fid, f in firms.items() if f.current_capacity > 0}

def place_student(student, firm):
    """Öğrenciyi firmaya yerleştir"""
    student.assigned_firm = firm.id
    student.is_placed = True
    firm.current_capacity -= 1
    firm.assigned_students.append(student.id)

def firm_rejection(students, firms, placed_this_iteration):
    """
    Firma reddetme mekanizması - %30 red olasılığı
    Reddedilen öğrenciler tekrar yerleşmemiş olur
    """
    rejected = []
    for student_id in placed_this_iteration:
        if random.random() < 0.30:  # %30 red olasılığı
            # Öğrenciyi bul
            student = next(s for s in students if s.id == student_id)
            firm = firms[student.assigned_firm]

            # Reddet
            student.is_placed = False
            student.assigned_firm = None
            firm.current_capacity += 1
            firm.assigned_students.remove(student_id)
            rejected.append(student_id)

    return rejected

def calculate_satisfaction_score(students):
    """
    Memnuniyet skoru hesapla
    1. tercih = 5 puan, 2. tercih = 4 puan, ..., 5. tercih = 1 puan
    Tercih dışı yerleşme = 0 puan
    """
    total_score = 0
    for s in students:
        if s.is_placed and s.assigned_firm:
            if s.assigned_firm in s.preferences:
                pref_index = s.preferences.index(s.assigned_firm)
                total_score += (5 - pref_index)  # 1. tercih = 5, 5. tercih = 1
            # Tercih dışı = 0 puan
    return total_score

# ==================== GREEDY ALGORİTMASI ====================

def greedy_algorithm(students, firms, log_callback=None):
    """
    Greedy (Açgözlü) Algoritma
    - Öğrenciler GNO'ya göre sıralanır
    - Her öğrenci tercihlerine sırayla bakar
    - İlk boş firmaya yerleşir
    """
    reset_data(students, firms)

    metrics = {
        'total_iterations': 0,
        'total_operations': 0,
        'start_time': time.time(),
        'phase_changes': [],
        'rejections': 0
    }

    current_phase = 1
    no_progress_count = 0

    def log(msg):
        if log_callback:
            log_callback(msg)

    log("=" * 50)
    log("GREEDY ALGORİTMASI BAŞLADI")
    log("=" * 50)

    while True:
        unplaced = get_unplaced_students(students)

        if not unplaced:
            log("\nTüm öğrenciler yerleşti!")
            break

        metrics['total_iterations'] += 1
        iteration = metrics['total_iterations']

        # GNO'ya göre sırala (yüksekten düşüğe)
        unplaced.sort(key=lambda x: x.gno, reverse=True)

        placed_this_iteration = []

        log(f"\n--- İterasyon {iteration} (Faz {current_phase}) ---")
        log(f"Yerleşmemiş öğrenci sayısı: {len(unplaced)}")

        for student in unplaced:
            available = get_available_firms(firms)

            if not available:
                break

            placed = False

            # FAZ 1 ve FAZ 2: Tercih bazlı yerleştirme
            if current_phase <= 2:
                # Önce tercihlere bak
                for pref in student.preferences:
                    metrics['total_operations'] += 1
                    if pref in available:
                        place_student(student, firms[pref])
                        placed_this_iteration.append(student.id)
                        placed = True
                        break

                # FAZ 2: Tercih dışı yerleştirme
                if not placed and current_phase == 2:
                    # Boş kontenjanı olan rastgele firmaya yerleştir
                    available_list = list(available.values())
                    if available_list:
                        random_firm = random.choice(available_list)
                        metrics['total_operations'] += 1
                        place_student(student, random_firm)
                        placed_this_iteration.append(student.id)
                        placed = True

            # FAZ 3: Zorunlu yerleştirme
            elif current_phase == 3:
                available_list = list(available.values())
                if available_list:
                    # İlk boş firmaya yerleştir
                    metrics['total_operations'] += 1
                    place_student(student, available_list[0])
                    placed_this_iteration.append(student.id)

        log(f"Bu iterasyonda yerleşen: {len(placed_this_iteration)}")

        # Firma reddetme (FAZ 3'te yok)
        if current_phase < 3 and placed_this_iteration:
            rejected = firm_rejection(students, firms, placed_this_iteration)
            metrics['rejections'] += len(rejected)
            if rejected:
                log(f"Reddedilen öğrenci sayısı: {len(rejected)}")

        # İlerleme kontrolü
        if len(placed_this_iteration) == 0:
            no_progress_count += 1
        else:
            no_progress_count = 0

        # Faz geçişleri
        if no_progress_count >= 5 and current_phase < 3:
            current_phase += 1
            no_progress_count = 0
            metrics['phase_changes'].append((iteration, current_phase))
            log(f"\n*** FAZ {current_phase}'e geçildi ***")

    metrics['end_time'] = time.time()
    metrics['total_time'] = metrics['end_time'] - metrics['start_time']
    metrics['satisfaction_score'] = calculate_satisfaction_score(students)

    log("\n" + "=" * 50)
    log("GREEDY SONUÇLARI")
    log("=" * 50)
    log(f"Toplam iterasyon: {metrics['total_iterations']}")
    log(f"Toplam işlem: {metrics['total_operations']}")
    log(f"Toplam süre: {metrics['total_time']:.4f} saniye")
    log(f"Memnuniyet skoru: {metrics['satisfaction_score']}")
    log(f"Toplam red sayısı: {metrics['rejections']}")

    return metrics

# ==================== HEURİSTİC ALGORİTMASI ====================

def calculate_match_score(student, firm, firms, is_preference):
    """
    Eşleşme skoru hesapla
    Tercih içi: Skor = (GNO × 0.4) + (Tercih × 0.3) + (Uygunluk × 0.3)
    Tercih dışı: Skor = (GNO × 0.4) + (Uygunluk × 0.3)
    """
    # GNO skoru (0-4 arası normalize edilmiş)
    gno_score = student.gno / 4.0

    # Tercih skoru
    if is_preference and firm.id in student.preferences:
        pref_index = student.preferences.index(firm.id)
        pref_score = (5 - pref_index) / 5.0  # 1. tercih = 1.0, 5. tercih = 0.2
    else:
        pref_score = 0

    # Uygunluk skoru (basit: firma kapasitesi bazlı)
    # Daha az dolu firmalar daha yüksek skor
    fill_ratio = 1 - (firm.current_capacity / firm.capacity) if firm.capacity > 0 else 0
    compat_score = 1 - fill_ratio  # Boş firmalar daha yüksek skor

    if is_preference:
        score = (gno_score * 0.4) + (pref_score * 0.3) + (compat_score * 0.3)
    else:
        score = (gno_score * 0.4) + (compat_score * 0.3)

    return score

def heuristic_algorithm(students, firms, log_callback=None):
    """
    Heuristic (Sezgisel) Algoritma
    - Puanlama tabanlı yerleştirme
    - En yüksek skorlu eşleşmeler öncelikli
    """
    reset_data(students, firms)

    metrics = {
        'total_iterations': 0,
        'total_operations': 0,
        'start_time': time.time(),
        'phase_changes': [],
        'rejections': 0
    }

    current_phase = 1
    no_progress_count = 0

    def log(msg):
        if log_callback:
            log_callback(msg)

    log("=" * 50)
    log("HEURİSTİC ALGORİTMASI BAŞLADI")
    log("=" * 50)

    while True:
        unplaced = get_unplaced_students(students)

        if not unplaced:
            log("\nTüm öğrenciler yerleşti!")
            break

        metrics['total_iterations'] += 1
        iteration = metrics['total_iterations']

        placed_this_iteration = []

        log(f"\n--- İterasyon {iteration} (Faz {current_phase}) ---")
        log(f"Yerleşmemiş öğrenci sayısı: {len(unplaced)}")

        # FAZ 1 ve FAZ 2: Skor bazlı yerleştirme
        if current_phase <= 2:
            # Tüm olası eşleşmeleri skorla
            matches = []

            for student in unplaced:
                available = get_available_firms(firms)

                if current_phase == 1:
                    # Sadece tercih listesindeki firmalar
                    candidate_firms = [f for f in student.preferences if f in available]
                else:
                    # Tüm firmalar
                    candidate_firms = list(available.keys())

                for firm_id in candidate_firms:
                    metrics['total_operations'] += 1
                    is_pref = firm_id in student.preferences
                    score = calculate_match_score(student, firms[firm_id], firms, is_pref)
                    matches.append((score, student, firms[firm_id]))

            # Skorlara göre sırala (yüksekten düşüğe)
            matches.sort(key=lambda x: x[0], reverse=True)

            # En yüksek skorlu eşleşmeleri yap
            placed_students = set()
            used_firms = set()

            for score, student, firm in matches:
                if student.id in placed_students:
                    continue
                if firm.id in used_firms and firm.current_capacity <= 0:
                    continue
                if firms[firm.id].current_capacity <= 0:
                    continue

                place_student(student, firms[firm.id])
                placed_this_iteration.append(student.id)
                placed_students.add(student.id)

                if firms[firm.id].current_capacity <= 0:
                    used_firms.add(firm.id)

        # FAZ 3: Zorunlu yerleştirme
        elif current_phase == 3:
            # GNO'ya göre sırala
            unplaced.sort(key=lambda x: x.gno, reverse=True)

            for student in unplaced:
                available = get_available_firms(firms)
                if available:
                    metrics['total_operations'] += 1
                    first_available = list(available.values())[0]
                    place_student(student, first_available)
                    placed_this_iteration.append(student.id)

        log(f"Bu iterasyonda yerleşen: {len(placed_this_iteration)}")

        # Firma reddetme (FAZ 3'te yok)
        if current_phase < 3 and placed_this_iteration:
            rejected = firm_rejection(students, firms, placed_this_iteration)
            metrics['rejections'] += len(rejected)
            if rejected:
                log(f"Reddedilen öğrenci sayısı: {len(rejected)}")

        # İlerleme kontrolü
        if len(placed_this_iteration) == 0:
            no_progress_count += 1
        else:
            no_progress_count = 0

        # Faz geçişleri
        if no_progress_count >= 5 and current_phase < 3:
            current_phase += 1
            no_progress_count = 0
            metrics['phase_changes'].append((iteration, current_phase))
            log(f"\n*** FAZ {current_phase}'e geçildi ***")

    metrics['end_time'] = time.time()
    metrics['total_time'] = metrics['end_time'] - metrics['start_time']
    metrics['satisfaction_score'] = calculate_satisfaction_score(students)

    log("\n" + "=" * 50)
    log("HEURİSTİC SONUÇLARI")
    log("=" * 50)
    log(f"Toplam iterasyon: {metrics['total_iterations']}")
    log(f"Toplam işlem: {metrics['total_operations']}")
    log(f"Toplam süre: {metrics['total_time']:.4f} saniye")
    log(f"Memnuniyet skoru: {metrics['satisfaction_score']}")
    log(f"Toplam red sayısı: {metrics['rejections']}")

    return metrics

# ==================== SONUÇ GÖSTERME ====================

def get_placement_details(students):
    """Yerleştirme detaylarını döndür"""
    details = []
    for s in students:
        if s.is_placed:
            pref_info = ""
            if s.assigned_firm in s.preferences:
                pref_num = s.preferences.index(s.assigned_firm) + 1
                pref_info = f"({pref_num}. tercih)"
            else:
                pref_info = "(tercih dışı)"
            details.append(f"{s.id} -> {s.assigned_firm} {pref_info}")
    return details

# ==================== GUI ====================

class SimulatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stajyer Yerleştirme Simülatörü")
        self.root.geometry("900x700")

        # Verileri yükle
        self.students = load_students()
        self.firms = load_firms()

        # Sonuçları sakla
        self.greedy_metrics = None
        self.heuristic_metrics = None
        self.greedy_placements = None
        self.heuristic_placements = None

        self.setup_ui()

    def setup_ui(self):
        # Üst frame - Butonlar
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.btn_greedy = tk.Button(
            btn_frame,
            text="Run Greedy",
            command=self.run_greedy,
            width=15,
            height=2
        )
        self.btn_greedy.pack(side=tk.LEFT, padx=10)

        self.btn_heuristic = tk.Button(
            btn_frame,
            text="Run Heuristic",
            command=self.run_heuristic,
            width=15,
            height=2
        )
        self.btn_heuristic.pack(side=tk.LEFT, padx=10)

        self.btn_compare = tk.Button(
            btn_frame,
            text="Compare Results",
            command=self.compare_results,
            width=15,
            height=2
        )
        self.btn_compare.pack(side=tk.LEFT, padx=10)

        # Notebook (sekmeli görünüm)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Log sekmesi
        log_frame = tk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Loglar")

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Yerleştirme sekmesi
        placement_frame = tk.Frame(self.notebook)
        self.notebook.add(placement_frame, text="Yerleştirmeler")

        self.placement_text = scrolledtext.ScrolledText(placement_frame, wrap=tk.WORD)
        self.placement_text.pack(fill=tk.BOTH, expand=True)

        # Karşılaştırma sekmesi
        compare_frame = tk.Frame(self.notebook)
        self.notebook.add(compare_frame, text="Karşılaştırma")

        self.compare_text = scrolledtext.ScrolledText(compare_frame, wrap=tk.WORD)
        self.compare_text.pack(fill=tk.BOTH, expand=True)

        # Bilgi etiketi
        info_label = tk.Label(
            self.root,
            text=f"Toplam {len(self.students)} öğrenci, {len(self.firms)} firma"
        )
        info_label.pack(pady=5)

    def log(self, message):
        """Log mesajı ekle"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def run_greedy(self):
        """Greedy algoritmasını çalıştır"""
        self.log_text.delete(1.0, tk.END)
        self.placement_text.delete(1.0, tk.END)

        # Verilerin yeni kopyasını al
        students = deepcopy(self.students)
        firms = deepcopy(self.firms)

        self.greedy_metrics = greedy_algorithm(students, firms, self.log)

        # Yerleştirmeleri kaydet
        self.greedy_placements = get_placement_details(students)

        # Yerleştirmeleri göster
        self.placement_text.insert(tk.END, "GREEDY YERLEŞTİRMELERİ\n")
        self.placement_text.insert(tk.END, "=" * 40 + "\n")
        for p in self.greedy_placements:
            self.placement_text.insert(tk.END, p + "\n")

        self.notebook.select(0)  # Log sekmesine geç

    def run_heuristic(self):
        """Heuristic algoritmasını çalıştır"""
        self.log_text.delete(1.0, tk.END)
        self.placement_text.delete(1.0, tk.END)

        # Verilerin yeni kopyasını al
        students = deepcopy(self.students)
        firms = deepcopy(self.firms)

        self.heuristic_metrics = heuristic_algorithm(students, firms, self.log)

        # Yerleştirmeleri kaydet
        self.heuristic_placements = get_placement_details(students)

        # Yerleştirmeleri göster
        self.placement_text.insert(tk.END, "HEURİSTİC YERLEŞTİRMELERİ\n")
        self.placement_text.insert(tk.END, "=" * 40 + "\n")
        for p in self.heuristic_placements:
            self.placement_text.insert(tk.END, p + "\n")

        self.notebook.select(0)  # Log sekmesine geç

    def compare_results(self):
        """İki algoritmanın sonuçlarını karşılaştır"""
        self.compare_text.delete(1.0, tk.END)

        if not self.greedy_metrics or not self.heuristic_metrics:
            self.compare_text.insert(tk.END, "Önce her iki algoritmayı da çalıştırın!\n")
            self.notebook.select(2)
            return

        # Karşılaştırma tablosu
        self.compare_text.insert(tk.END, "=" * 60 + "\n")
        self.compare_text.insert(tk.END, "         GREEDY vs HEURİSTİC KARŞILAŞTIRMA\n")
        self.compare_text.insert(tk.END, "=" * 60 + "\n\n")

        headers = f"{'Metrik':<25} {'Greedy':>15} {'Heuristic':>15}\n"
        self.compare_text.insert(tk.END, headers)
        self.compare_text.insert(tk.END, "-" * 55 + "\n")

        # Metrikleri karşılaştır
        metrics_to_compare = [
            ("Toplam İterasyon", 'total_iterations'),
            ("Toplam İşlem", 'total_operations'),
            ("Çalışma Süresi (sn)", 'total_time'),
            ("Memnuniyet Skoru", 'satisfaction_score'),
            ("Toplam Red", 'rejections'),
        ]

        for label, key in metrics_to_compare:
            g_val = self.greedy_metrics[key]
            h_val = self.heuristic_metrics[key]

            if key == 'total_time':
                row = f"{label:<25} {g_val:>15.4f} {h_val:>15.4f}\n"
            else:
                row = f"{label:<25} {g_val:>15} {h_val:>15}\n"

            self.compare_text.insert(tk.END, row)

        self.compare_text.insert(tk.END, "-" * 55 + "\n")

        # Kazanan analizi
        self.compare_text.insert(tk.END, "\nANALİZ:\n")

        # İterasyon
        if self.greedy_metrics['total_iterations'] < self.heuristic_metrics['total_iterations']:
            self.compare_text.insert(tk.END, "- İterasyon: Greedy daha az iterasyonla tamamladı\n")
        elif self.greedy_metrics['total_iterations'] > self.heuristic_metrics['total_iterations']:
            self.compare_text.insert(tk.END, "- İterasyon: Heuristic daha az iterasyonla tamamladı\n")
        else:
            self.compare_text.insert(tk.END, "- İterasyon: Eşit\n")

        # İşlem
        if self.greedy_metrics['total_operations'] < self.heuristic_metrics['total_operations']:
            self.compare_text.insert(tk.END, "- İşlem sayısı: Greedy daha az işlem yaptı\n")
        elif self.greedy_metrics['total_operations'] > self.heuristic_metrics['total_operations']:
            self.compare_text.insert(tk.END, "- İşlem sayısı: Heuristic daha az işlem yaptı\n")
        else:
            self.compare_text.insert(tk.END, "- İşlem sayısı: Eşit\n")

        # Süre
        if self.greedy_metrics['total_time'] < self.heuristic_metrics['total_time']:
            self.compare_text.insert(tk.END, "- Süre: Greedy daha hızlı\n")
        else:
            self.compare_text.insert(tk.END, "- Süre: Heuristic daha hızlı\n")

        # Memnuniyet
        if self.greedy_metrics['satisfaction_score'] > self.heuristic_metrics['satisfaction_score']:
            self.compare_text.insert(tk.END, "- Memnuniyet: Greedy daha yüksek memnuniyet sağladı\n")
        elif self.greedy_metrics['satisfaction_score'] < self.heuristic_metrics['satisfaction_score']:
            self.compare_text.insert(tk.END, "- Memnuniyet: Heuristic daha yüksek memnuniyet sağladı\n")
        else:
            self.compare_text.insert(tk.END, "- Memnuniyet: Eşit\n")

        self.notebook.select(2)  # Karşılaştırma sekmesine geç

    def run(self):
        """GUI'yi başlat"""
        self.root.mainloop()

# ==================== ANA PROGRAM ====================

if __name__ == "__main__":
    app = SimulatorGUI()
    app.run()