import sys
import os
import chess
import chess.pgn
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QPushButton, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QSize



class ChessBoardGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess PGN Viewer")
        self.setGeometry(100, 100, 600, 600)

        # Load chess assets
        self.assets_path = "assets"
        self.board = chess.Board()
        self.current_move_index = -1
        self.moves = []
        self.white_player = ""
        self.black_player = ""
        self.white_rating = ""
        self.black_rating = ""
        self.termination = ""
        self.is_flipped = False  # Track board orientation

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        self.white_label = QLabel("White: ")
        self.layout.addWidget(self.white_label, 0, 0, 1, 4)

        self.black_label = QLabel("Black: ")
        self.layout.addWidget(self.black_label, 0, 4, 1, 4)

        self.white_rating_label = QLabel("White Rating: ")
        self.layout.addWidget(self.white_rating_label, 1, 0, 1, 4)

        self.black_rating_label = QLabel("Black Rating: ")
        self.layout.addWidget(self.black_rating_label, 1, 4, 1, 4)

        self.termination_label = QLabel("Termination: ")
        self.layout.addWidget(self.termination_label, 2, 0, 1, 8)

        self.chessboard_widget = ChessBoardWidget(self)
        self.layout.addWidget(self.chessboard_widget, 3, 0, 1, 8)

        self.previous_button = QPushButton("Previous")
        self.previous_button.clicked.connect(self.show_previous_move)
        self.layout.addWidget(self.previous_button, 4, 0, 1, 2)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_move)
        self.layout.addWidget(self.next_button, 4, 2, 1, 2)

        self.flip_button = QPushButton("Flip Board")  # Add flip button
        self.flip_button.clicked.connect(self.flip_board)
        self.layout.addWidget(self.flip_button, 4, 4, 1, 4)

    def load_pgn(self, pgn_path):
        with open(pgn_path, "r") as pgn_file:
            game = chess.pgn.read_game(pgn_file)
            self.moves = list(game.mainline_moves())
            self.white_player = game.headers.get("White", "Unknown")
            self.black_player = game.headers.get("Black", "Unknown")
            self.white_rating = game.headers.get("WhiteElo", "Unknown")
            self.black_rating = game.headers.get("BlackElo", "Unknown")
            self.termination = game.headers.get("Termination", "Unknown")

            self.white_label.setText(f"White: {self.white_player}")
            self.black_label.setText(f"Black: {self.black_player}")
            self.white_rating_label.setText(f"White Rating: {self.white_rating}")
            self.black_rating_label.setText(f"Black Rating: {self.black_rating}")
            self.termination_label.setText(f"Termination: {self.termination}")

        self.chessboard_widget.update_board()

    def show_next_move(self):
        if self.current_move_index < len(self.moves) - 1:
            self.current_move_index += 1
            self.board.push(self.moves[self.current_move_index])
            self.chessboard_widget.update_board()

    def show_previous_move(self):
        if self.current_move_index >= 0:
            self.board.pop()
            self.current_move_index -= 1
            self.chessboard_widget.update_board()

    def flip_board(self):
        self.is_flipped = not self.is_flipped  # Toggle board orientation
        self.chessboard_widget.update_board()


class ChessBoardWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def sizeHint(self):
        return QSize(600, 600)  # Ensure the widget size does not exceed 600x600

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw_board(qp)
        qp.end()

    def draw_board(self, qp):
        size = self.size()
        square_size = min(size.width(), size.height()) // 8

        # Calculate offsets to center the board
        board_size = square_size * 8
        x_offset = (size.width() - board_size) // 2
        y_offset = (size.height() - board_size) // 2

        for row in range(8):
            for col in range(8):
                color = Qt.lightGray if (row + col) % 2 == 0 else Qt.gray
                qp.setBrush(QBrush(color))
                qp.drawRect(
                    x_offset + col * square_size, 
                    y_offset + row * square_size, 
                    square_size, 
                    square_size
                )

                display_row = 7 - row if self.parent.is_flipped else row  # Flip rows if needed
                display_col = 7 - col if self.parent.is_flipped else col  # Flip columns if needed
                square = chess.square(display_col, 7 - display_row)
                piece = self.parent.board.piece_at(square)
                if piece:
                    piece_color = "d" if piece.color == chess.WHITE else "l"
                    piece_type = chess.PIECE_SYMBOLS[piece.piece_type]
                    piece_name = f"Chess_{piece_type}{piece_color}t60.png"
                    piece_path = os.path.join(self.parent.assets_path, piece_name)
                    pixmap = QPixmap(piece_path).scaled(square_size, square_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    qp.drawPixmap(
                        x_offset + col * square_size + (square_size - pixmap.width()) // 2, 
                        y_offset + row * square_size + (square_size - pixmap.height()) // 2, 
                        pixmap
                    )

    def update_board(self):
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ChessBoardGUI()

    # Load a sample PGN file
    viewer.load_pgn("sample.pgn")  # Replace with your PGN file path
    viewer.show()
    sys.exit(app.exec_())