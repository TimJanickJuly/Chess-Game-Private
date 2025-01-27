from browser import document, html, ajax, websocket, alert, window
import json

class Config:
    BASE_URL = "http://localhost:8000"

class GameState:
    def __init__(self):
        self.text = "Waiting for game to start..."
        self.code = 0
        self.details = None
        self.board_state = [
            [-5, -3, -4, -9, -10, -4, -3, -5],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [5, 3, 4, 9, 10, 4, 3, 5]
        ]
        self.legal_moves = []
        self.player_name = ""
        self.player_color = None
        self.game_id = None
        self.num_moves_played = 0
        self.active_player = ""
        self.players = []
        self.player_colors = {}
        self.both_joined = False
        self.piece_encoding = {
            -10: "bK", -9: "bQ", -5: "bR", -4: "bB", -3: "bN", -1: "bP", 
            0: None,
            1: "wP", 3: "wN", 4: "wB", 5: "wR", 9: "wQ", 10: "wK"
        }
        self.board_state = [
                    [-5, -3, -4, -9, -10, -4, -3, -5],
                    [-1, -1, -1, -1, -1, -1, -1, -1],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [5, 3, 4, 9, 10, 4, 3, 5]
                ]

    def update_from_response(self, response):
        self.text = response.get("game_state", self.text)
        self.num_moves_played = response.get("num_moves_played", self.num_moves_played)
        self.active_player = response.get("active_player", self.active_player)
        self.players = response.get("players", self.players)
        self.player_colors = response.get("player_colors", self.player_colors)
        self.both_joined = response.get("both_joined", self.both_joined)
        self.board_state = response.get("board_state", self.board_state)
        self.legal_moves = response.get("legal_moves", self.legal_moves)
        self.debug_state()
        
    def debug_state(self):
        print("GameState Debug:")
        print(f"  Text: {self.text}")
        print(f"  Player ID: {self.player_name}")
        print(f"  Game ID: {self.game_id}")
        print(f"  Num Moves Played: {self.num_moves_played}")
        print(f"  Active Player: {self.active_player}")
        print(f"  Players: {self.players}")
        print(f"  Player Colors: {self.player_colors}")
        print(f"  Both Joined: {self.both_joined}")
        print(f"  Board State: {self.board_state}")
        print(f"  Legal Moves: {self.legal_moves}")
        
    def generate_player_name(self):
        random_string = ''.join(
            chr(97 + (x % 26)) for x in window.crypto.getRandomValues(window.Uint8Array.new(16))
        )
        return f"player_{random_string}"
        
class WebSocketHandler:
    def __init__(self, game_state):
        self.socket = None
        self.socket_open = False
        self.game_state = game_state

    def connect(self):
        if not self.game_state.game_id or not self.game_state.player_name:
            print("Cannot connect: Game ID or Player Name is missing.")
            return

        try:
            self.socket = websocket.WebSocket(f"ws://localhost:8000/ws/{self.game_state.game_id}/{self.game_state.player_name}")
            self.socket.bind("open", self.on_open)
            self.socket.bind("message", self.on_message)
            self.socket.bind("close", self.on_close)
        except Exception as e:
            print(f"Failed to establish WebSocket connection: {e}")

    def on_open(self, event):
        self.socket_open = True
        print("WebSocket connection established.")

    def on_message(self, event):
        try:
            data = json.loads(event.data)
            if data.get("event") == "state":
                state = data.get("state", {})
                if not state:
                    print("Invalid state data received.")
                    return
                
                self.game_state.update_from_response(state)
                UI.update(self.game_state.board_state)
                UI.update_game_state(self.game_state.text)
            else:
                print(f"Unhandled event type: {data.get('event')}")
        except json.JSONDecodeError:
            print("Failed to parse WebSocket message.")
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")

    def on_close(self, event):
        self.socket_open = False
        print("WebSocket disconnected. Attempting to reconnect in 5 seconds...")
        window.setTimeout(self.connect, 5000)  # Verzögere den Reconnect-Versuch um 5 Sekunden

    
    def request_game_state(self):
        if not self.socket or not self.socket_open:
            print("WebSocket connection is not active. Cannot request game state.")
            return

        try:
            self.socket.send(json.dumps({"action": "get_state"}))
        except Exception as e:
            print(f"Failed to request game state: {e}")


    def send_move(self, start, end):
        if not self.socket or not self.socket_open:
            print("WebSocket connection is not active. Move cannot be sent.")
            # Optional: Füge eine Warteschlange hinzu, um Züge später zu senden
            return

        try:
            move_data = {
                "action": "move",
                "move": {"start": {"row": start[0], "col": start[1]}, "end": {"row": end[0], "col": end[1]}}
            }
            self.socket.send(json.dumps(move_data))
        except Exception as e:
            print(f"Failed to send move: {e}")  

class API:
    @staticmethod
    def create_game(game_state):
        url = Config.BASE_URL + "/create_game"
        print(f"Creating game with URL: {url}")
        ajax.post(
            url,
            oncomplete=lambda req: API._handle_create_game(req, game_state)
        )

    @staticmethod
    def _handle_create_game(req, game_state):
        if req.status == 200:
            try:
                response = json.loads(req.text)
                game_state.game_id = response.get("game_id")
                if not game_state.game_id:
                    print("Game ID missing in the server response.")
                    return

                print(f"Game created with ID: {game_state.game_id}")
                API.join_game(game_state)
            except json.JSONDecodeError:
                print("Failed to parse server response as JSON.")
        else:
            print(f"Failed to create game: HTTP {req.status}")


    @staticmethod
    def join_game(game_state):
        if not game_state.game_id or not game_state.player_name:
            print("Cannot join game: Game ID or Player Name is missing.")
            return
        
        game_state.debug_state()

        url = Config.BASE_URL + f"/join_game/{game_state.game_id}"
        data = {"player_id": game_state.player_name}

        def handle_response(req):
            if req.status == 200:
                try:
                    response = json.loads(req.text)
                    print(f"Successfully joined game. Response: {response}")
                    game_state.both_joined = response.get("both_joined", False)
                except json.JSONDecodeError:
                    print("Failed to parse server response for join_game.")
            else:
                print(f"Failed to join game: HTTP {req.status}. Response: {req.text}")

        ajax.post(
            url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            oncomplete=handle_response
        )

class EventBindings:
    @staticmethod
    def bind_events():
        document["gameIdInput"].bind("keydown", EventBindings.process_input)
        document["showInputBtn"].bind("click", EventBindings.show_input_field)
        document["createGameBtn"].bind("click", lambda event: game_init("create"))

    @staticmethod
    def show_input_field(event):
        input_field = document["gameIdInput"]
        if not input_field:
            print("Error: 'gameIdInput' not found in the DOM.")
            return

        if input_field.style.display == "none":
            input_field.style.display = "block"
            input_field.focus()
        else:
            print("Input field is already visible.")

    @staticmethod
    def process_input(event):
        if event.keyCode == 13:  # Enter key
            input_field = document["gameIdInput"]
            if not input_field:
                print("Error: 'gameIdInput' not found in the DOM.")
                return

            game_id = input_field.value.strip()
            if game_id:
                print(f"Game ID entered: {game_id}")
                API.join_game(game_state)
            else:
                alert("Please enter a valid Game ID!")


class UI:
    @staticmethod
    def create_chessboard():
        board = document["board"] 
        if not board:
            print("Error: Chessboard container not found in the DOM.")
            return

        board.style.display = "grid"
        board.style.gridTemplateRows = board.style.gridTemplateColumns = "repeat(8, 60px)"
        colors = ["white", "black"]

        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                square = html.DIV(Class=f"square {color}", Id=f"{row}{col}")
                board <= square

        for btn_id in ["createGameBtn", "showInputBtn", "gameIdInput"]:
            element = document[btn_id]  # Auch hier wird document[...]-Syntax verwendet
            if element:
                element.style.display = "none"
            else:
                print(f"Warning: Element '{btn_id}' not found in the DOM.")

    @staticmethod
    def update_game_state(new_state):
        game_state_element = document["gameState"]
        if game_state_element:
            game_state_element.text = new_state
        else:
            print("Error: 'gameState' element not found in the DOM.")

    @staticmethod
    def place_piece(row, col, piece):
        position = f"{row}{col}"
        square = document[position]
        if not square:
            print(f"Error: Square {position} not found in the DOM.")
            return

        for child in square.children:
            if child.Class == "piece":
                square.remove(child)

        if piece:
            img = html.IMG(src=f"./libs/img/chesspieces/wikipedia/{piece}.png", Class="piece", draggable="true")
            img.bind("dragstart", UI.drag_start)
            square <= img

    @staticmethod
    def update_board_state(board_state):
        if not board_state or len(board_state) != 8 or any(len(row) != 8 for row in board_state):
            print("Error: Invalid board_state provided.")
            return

        for row in range(8):
            for col in range(8):
                position = f"{row}{col}"
                square = document[position]
                if square:
                    for child in list(square.children):
                        if child.Class == "piece":
                            square.remove(child)

        for row in range(8):
            for col in range(8):
                piece = game_state.piece_encoding.get(board_state[row][col])
                if piece is None and board_state[row][col] != 0:
                    print(f"Warning: Unrecognized piece code at ({row}, {col}).")
                UI.place_piece(row, col, piece)

    @staticmethod
    def add_drag_and_drop():
        for row in range(8):
            for col in range(8):
                square_id = f"{row}{col}"
                square = document[square_id]
                if not square:
                    print(f"Warning: Square {square_id} not found in the DOM.")
                    continue

                square.bind("dragover", UI.allow_drop)
                square.bind("drop", UI.drop)

    @staticmethod
    def allow_drop(event):
        print("allow_drop triggered")
        event.preventDefault()

    @staticmethod
    def drag_start(event):
        print("drag_start triggered")
        parent_id = event.target.parent.id if event.target.parent else None
        if parent_id:
            event.dataTransfer.setData("text", parent_id)
        else:
            print("Warning: drag_start failed due to missing parent ID.")

    @staticmethod
    def drop(event):
        print("drop triggered")
        event.preventDefault()
        source_square_id = event.dataTransfer.getData("text")
        target_square_id = event.target.id

        if not source_square_id or not target_square_id:
            print("Error: Invalid drag-and-drop data.")
            return

        print(f"Source: {source_square_id}, Target: {target_square_id}")
        if source_square_id != target_square_id:
            try:
                start_row, start_col = int(source_square_id[0]), int(source_square_id[1])
                end_row, end_col = int(target_square_id[0]), int(target_square_id[1])

                if (start_row, start_col, end_row, end_col) not in game_state.legal_moves:
                    print("Illegal move attempted.")
                    return

                print(f"Moving piece from ({start_row}, {start_col}) to ({end_row}, {end_col})")
                source_square = document[source_square_id]
                if source_square and source_square.firstChild:
                    event.target.appendChild(source_square.firstChild)
                    socket_handler.send_move((start_row, start_col), (end_row, end_col))
                else:
                    print(f"Error: No piece to move from {source_square_id}.")
            except ValueError:
                print("Error: Invalid square IDs.")


game_state = GameState()
socket_handler = WebSocketHandler(game_state)
EventBindings.bind_events()

def game_init(mode):
    UI.create_chessboard()
    UI.add_drag_and_drop()
    game_state.player_name = game_state.generate_player_name()
    if mode == "create":
        API.create_game(game_state)
    API.join_game(game_state)
    UI.update_board_state(game_state.board_state)
    socket_handler.connect()
