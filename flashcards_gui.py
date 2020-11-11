#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QLineEdit, QComboBox, QProgressBar, QSizePolicy, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette
import time
from datetime import datetime
import flashcards as fc
import os, yaml
from pathlib import Path
import appdirs


class FlashCards:
    config_path = Path(appdirs.user_config_dir('flashcards'))

    def __init__(self):
        self.app = QApplication([])
        font = self.app.font()
        font.setBold(True)
        font.setPointSize(2 * font.pointSize())
        self.app.setFont(font)
        self.window = QWidget()
        FlashCards.config_path.mkdir(parents=True, exist_ok=True)
        self.configs = self.load_configs()
        self.current_config = self.configs[0]
        layout = self.home()
        self.window.setLayout(layout)
        self.window.show()
        self.app.exec()

    def save_config(self):
        file = FlashCards.config_path / (self.current_config["name"] + ".yml")
        with open(file, "w") as ymlfile:
            config = self.current_config.copy()
            config['log_file_dir'] = str(config['log_file_dir'])
            yaml.dump(config, ymlfile)

    def delete_config(self):
        file = FlashCards.config_path / (self.current_config["name"] + ".yml")
        os.remove(file)

    def save_log(self):
        now = datetime.now()
        dt_str = now.strftime("%Y%m%dT%H%M%S")
        file = self.current_config['log_file_dir'] / ("FlashCardsLog_" + self.current_config["name"] + "_" + dt_str + ".txt")
        file.write_text(self.deck.worst_cards())

    def save_deck(self):
        now = datetime.now()
        dt_str = now.strftime("%Y%m%dT%H%M%S")
        file = self.current_config['log_file_dir'] / ("FlashCardDeck_" + self.current_config["name"] + "_" + dt_str + ".yml")
        with open(file, 'w') as ymlfile:
            yd = self.deck.as_yaml_dict()
            yaml.dump(yd, ymlfile)

    def load_configs(self):
        default = {
            "mastery_time": 5,
            "min_val": 0,
            "max_val": 12,
            "name": "Default",
            "log_file_dir": Path.home() / 'Desktop'
        }

        # get all yaml files in the config directory
        config_files = [cfg for cfg in FlashCards.config_path.iterdir() if cfg.name.endswith(".yml")]

        configs = []
        for f in config_files:
            with open(f, "r") as ymlfile:
                config = yaml.load(ymlfile, Loader=yaml.SafeLoader)
                # upgrade old config files
                if 'log_file_dir' not in config:
                    config['log_file_dir'] = Path.home() / 'Desktop'
                else:
                    config['log_file_dir'] = Path(config['log_file_dir'])
                configs.append(config)
        print(configs)

        if len(configs) == 0:
            configs.append(default)
        return configs


    def home(self):
        self.configs = self.load_configs()
        def on_addition_clicked():
            update_config()
            self.save_config()
            self.deck = fc.generate_addition(min_val.value(), max_val.value(), time_threshold=mastery_time.value())
            self.run_deck()

        def on_subtraction_clicked():
            update_config()
            self.save_config()
            self.deck = fc.generate_subtraction(min_val.value(), max_val.value(), time_threshold=mastery_time.value())
            self.run_deck()

        def on_multiplication_clicked():
            update_config()
            self.save_config()
            self.deck = fc.generate_multiplication(min_val.value(), max_val.value(), time_threshold=mastery_time.value())
            self.run_deck()

        def on_division_clicked():
            update_config()
            self.save_config()
            self.deck = fc.generate_division(min_val.value(), max_val.value(), time_threshold=mastery_time.value())
            self.run_deck()

        def on_custom_clicked():
            update_config()
            self.save_config()
            file, _ = QFileDialog.getOpenFileName(self.window, "Open Flashcard Deck", str(self.current_config["log_file_dir"]), "Flashcard decks (*.yml)")
            self.deck = fc.load_deck(file)
            for c in self.deck.cards:
                c.responses = []
            self.run_deck()

        def update_config():
            self.current_config["name"] = config_name.currentText()
            self.current_config["mastery_time"] = mastery_time.value()
            self.current_config["min_val"] = min_val.value()
            self.current_config["max_val"] = max_val.value()

        def on_config_change():
            print(config_name.currentIndex())
            config = self.configs[config_name.currentIndex()]
            mastery_time.setValue(config["mastery_time"])
            min_val.setValue(config["min_val"])
            max_val.setValue(config["max_val"])
            self.current_config = config

        def on_range_change():
            min_val.setRange(0, max_val.value())
            max_val.setRange(min_val.value(), 25)

        def update_configs():
            config_name.clear()
            for cfg in self.configs:
                config_name.addItem(cfg["name"])
            config_name.setCurrentText(self.current_config["name"])

        def remove_config():
            if self.current_config["name"] == config_name.currentText():
                self.delete_config()
                config_name.removeItem(config_name.currentIndex())

        layout = QVBoxLayout()
        layout.addStretch()
        layout_config = QHBoxLayout()
        add_config = QPushButton('Add Config')
        add_config.setMaximumWidth(400)
        layout_config.addWidget(add_config)
        config_name = QComboBox()
        update_configs()
        config_name.currentTextChanged.connect(on_config_change)
        add_config.clicked.connect(lambda _: (config_name.setEditable(True), config_name.clearEditText()))
        layout_config.addWidget(config_name)
        rm_config = QPushButton('Remove Config')
        rm_config.setMaximumWidth(500)
        rm_config.clicked.connect(remove_config)
        layout_config.addWidget(rm_config)
        layout.addLayout(layout_config)
        layout.addStretch()

        layout_mastery_time = QHBoxLayout()
        layout_mastery_time.addWidget(QLabel("Response time for a problem to be mastered (seconds)"))
        mastery_time = QSpinBox()
        mastery_time.setRange(1, 15)
        mastery_time.setValue(self.current_config["mastery_time"])
        layout_mastery_time.addWidget(mastery_time)
        layout.addLayout(layout_mastery_time)

        layout.addStretch()

        layout_min = QHBoxLayout()
        layout_min.addWidget(QLabel("Minimum Value"))
        min_val = QSpinBox()
        min_val.setRange(0, 25)
        min_val.setValue(self.current_config["min_val"])
        layout_min.addWidget(min_val)
        layout.addLayout(layout_min)

        layout_max = QHBoxLayout()
        layout_max.addWidget(QLabel("Maximum Value"))
        max_val = QSpinBox()
        max_val.setRange(1, 25)
        max_val.setValue(self.current_config["max_val"])
        layout_max.addWidget(max_val)
        layout.addLayout(layout_max)

        min_val.valueChanged.connect(on_range_change)
        max_val.valueChanged.connect(on_range_change)

        type_selection_layout = QHBoxLayout()
        type_selection_layout.addWidget(QLabel("Select type of flashcards:"))

        button_layout = QVBoxLayout()
        addition = QPushButton("Addition")
        subtraction = QPushButton("Subtraction")
        multiplication = QPushButton("Multiplication")
        division = QPushButton("Division")
        custom = QPushButton("Load from File")
        addition.clicked.connect(on_addition_clicked)
        subtraction.clicked.connect(on_subtraction_clicked)
        multiplication.clicked.connect(on_multiplication_clicked)
        division.clicked.connect(on_division_clicked)
        custom.clicked.connect(on_custom_clicked)
        button_layout.addWidget(addition)
        button_layout.addWidget(subtraction)
        button_layout.addWidget(multiplication)
        button_layout.addWidget(division)
        button_layout.addWidget(custom)
        type_selection_layout.addLayout(button_layout)

        layout.addStretch()
        layout.addLayout(type_selection_layout)
        layout.addStretch()
        return layout

    def run_deck(self):
        def go_home():
            self.window.close()
            self.window = QWidget()
            layout = self.home()
            self.window.setLayout(layout)
            self.window.show()

        def on_answer_given():
            if not self.incorrect_delay:
                result = self.current_card.log_response(answer.text().strip(), time.time() - self.t0)
                if result == fc.Card.Result.INCORRECT:
                    answer.setText("Incorrect!")
                    answer.setDisabled(True)
                    # problem.setText(f"{problem.text()}\n\nIncorrect!")
                    self.incorrect_delay = True
                    delay_time = min(int(2 * (time.time() - self.t0) * 1000), self.deck.time_threshold * 1000)
                    QTimer.singleShot(delay_time, on_answer_given)
                    # warning - the program crashes if the user tries to enter another answer during this delay
                    return
                elif result == fc.Card.Result.INVALID:
                    QMessageBox.critical(self.window, "                     Invalid response!                        ", f"Invalid response ({answer.text()}); try again.")
                    answer.setText("")
                    return
            else:
                self.incorrect_delay = False
                answer.setDisabled(False)
            answer.setText("")
            completed, total = self.deck.progress()
            self.progressBar.setValue(completed)
            self.progressLabel.setText(f'{total - completed} cards remaining')
            if completed < total:
                self.current_card = self.deck.get_card()
                self.t0 = time.time()
                problem.setText(self.current_card.get_problem()[0])
                answer.setFocus()
            else:
                problem.setFont(self.smallerFont)
                problem.setText(self.deck.worst_cards())
                problem.setTextInteractionFlags(Qt.TextSelectableByMouse)
                answer.deleteLater()
                self.save_log()
                self.save_deck()


        self.current_card = self.deck.get_card()
        self.t0 = time.time()
        self.incorrect_delay = False
        layout = QVBoxLayout()
        home = QPushButton('Give up and go home')
        self.smallerFont = self.window.font()
        self.smallerFont.setPointSize(self.smallerFont.pointSize() // 2)
        home.setFont(self.smallerFont)
        home.clicked.connect(go_home)
        layout.addWidget(home)
        layout.addStretch()
        problem = QLabel(self.current_card.get_problem()[0])
        layout.addWidget(problem)
        layout.addStretch()
        answer = QLineEdit()
        answer.returnPressed.connect(on_answer_given)
        layout.addWidget(answer)
        layout.addStretch()
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, len(self.deck.cards))
        self.progressLabel = QLabel(f'{len(self.deck.cards)} cards remaining')
        self.progressBar.setFont(self.smallerFont)
        self.progressLabel.setFont(self.smallerFont)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.progressLabel)
        layout.addStretch()
        self.window.close()
        self.window = QWidget()
        self.window.setLayout(layout)
        self.window.show()
        answer.setFocus()



if __name__ == "__main__":
    fc = FlashCards()

