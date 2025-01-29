from browser import document, html, ajax, websocket, alert, window, bind
import json

class Config:
    BASE_URL = "http://localhost:8000"

class GameState:
    def __init__(self):
        self.text = "Waiting for game to start..."
        self.game_status = "waiting"
        self.code = 0
        self.details = None
        self.own_color = None
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
            0: "empty",
            1: "wP", 3: "wN", 4: "wB", 5: "wR", 9: "wQ", 10: "wK"
        }

    def update_from_response(self, response):
        self.game_status = response.get("game_state", self.game_status)
        self.num_moves_played = response.get("num_moves_played", self.num_moves_played)
        self.active_player = response.get("active_player", self.active_player)
        self.players = response.get("players", self.players)
        self.player_colors = response.get("player_colors", self.player_colors)
        self.both_joined = response.get("both_joined", self.both_joined)
        self.board_state = response.get("board_state", self.board_state)
        self.legal_moves = response.get("legal_moves", self.legal_moves)
        if not self.own_color:
            self.own_color = self.player_colors.get(self.player_name, None)
        if not self.both_joined:
            self.text = "Waiting for Opponent"
        else:
            self.text = f"It's {self.player_colors[self.active_player]}'s turn!"
        print("Updated Game state: ")
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
        print(f"own_color:  {self.own_color}")
        print(f"  Both Joined: {self.both_joined}")
        print(f"  Legal Moves: {self.legal_moves}")
        
    def generate_player_name(self):
        random_string = ''.join(
            chr(97 + (x % 26)) for x in window.crypto.getRandomValues(window.Uint8Array.new(16))
        )
        return f"player_{random_string}"

        
    def is_move_legal(
        self,
        row_start = None,
        col_start = None,
        row_end = None,
        col_end = None
        ):
        print("Legal Check")
        print(f"start row = {(7 - row_start) % 8}, start col = {col_start}")
        print(f"end row = {(7 - row_end) % 8}, end col = {col_end}")
        
        print("Found piece on start square: ", self.board_state[row_start][col_start])
        
        if self.active_player != self.player_name:
            print("illegal: its not your turn")
            return False
        
        own_piece_enocding = 1 if self.own_color == "white" else -1
        if self.board_state[row_start][col_start] * own_piece_enocding <= 0:
            print("illegale: not your piece")
            return False 
        
        print("Searching move")
        print("searching for", [(7 - row_start) % 8, col_start])
        print(row_start, col_start, row_end, col_end, self.own_color, row_start and col_start and row_end and col_end and self.own_color)
        if row_start is not None and col_start is not None and row_end is not None and col_end is not None and self.own_color:
            for piece_type, start_square, end_squares in self.legal_moves.get(self.own_color, []):
                print(piece_type, start_square, end_squares)
                if start_square == [(7 - row_start) % 8, col_start]:
                    if [(7 - row_end) % 8, col_end] in end_squares:
                        print("move is legal!")
                        return True
        
class WebSocketHandler:
    def __init__(self, game_state):
        self.socket = None
        self.socket_open = False
        self.game_state = game_state

    def connect(self):
        if not self.game_state.game_id or not self.game_state.player_name:
            print("DEBUG", self.game_state.debug_state())
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
        print("Received message")
        try:
            data = json.loads(event.data)
            if data.get("event") == "state" or data.get("event") == "update":
                state = data.get("state", {})
                if not state:
                    print("Invalid state data received.")
                    return
                print("Received new game state:", state)
                self.game_state.update_from_response(state)
                UI.update_board_state(self.game_state.board_state)
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
            print("Move sucessfully")
        except Exception as e:
            print(f"Failed to send move: {e}")  
            
            

class API:
    @staticmethod
    def can_i_join(game_id, callback):
        url = Config.BASE_URL + f"/game_info/{game_id}"
        print(f"Asking whether I can join: {url}")

        # Asynchroner Ajax-Request
        def handle_response(response):
            if response.status == 200:
                try:
                    game_info = json.loads(response.text)
                    print(game_info)
                    joinable = not game_info.get("both_joined", False)
                    callback(joinable)  # Ergebnis an die Callback-Funktion übergeben
                except Exception as e:
                    print(f"Error processing game info: {e}")
                    callback(False)
            else:
                print(f"Error: HTTP {response.status}")
                callback(False)

        # ajax.get ohne `oncomplete` wird standardmäßig asynchron verarbeitet
        ajax.get(url, oncomplete=handle_response)
        
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
                API.join_game(game_state, callback=lambda: (
                    socket_handler.connect(),
                    UI.display_game_id(game_state.game_id)
                    ))
            except json.JSONDecodeError:
                print("Failed to parse server response as JSON.")
        else:
            print(f"Failed to create game: HTTP {req.status}")


    @staticmethod
    def join_game(game_state, callback=None):
        if not game_state.game_id or not game_state.player_name:
            print("Cannot join game: Game ID or Player Name is missing.")
            return

        url = Config.BASE_URL + f"/join_game/{game_state.game_id}"
        data = {"player_id": game_state.player_name}

        def handle_response(req):
            if req.status == 200:
                try:
                    response = json.loads(req.text)
                    print(f"Successfully joined game. Response: {response}")
                    game_state.both_joined = response.get("both_joined", False)
                    if callback:
                        callback()
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
            
            print("Trying to join: ", game_id)
            
            if game_id:
                def handle_can_i_join_response(joinable):
                    if joinable:
                        print(f"Game ID entered: {game_id}")
                        game_state.game_id = game_id
                        game_init()
                    else:
                        alert("Game is full or cannot be joined.")

                # Übergabe der Callback-Funktion an `can_i_join`
                API.can_i_join(game_id, callback=handle_can_i_join_response)
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
        print("Piece placed")
        position = f"{row}{col}"
        square = document[position]
        if not square:
            print(f"Error: Square {position} not found in the DOM.")
            return
        
        def has_piece(square):
            for child in square.children:
                if child.tagName.lower() == "img" and "piece" in child.attrs.get("class", "").split():
                    return True
            return False
                       
        if has_piece(square):
            for child in list(square.children):
                if child.tagName.lower() == "img" and "piece" in child.attrs.get("class", "").split():
                    child.attrs["src"] = f"./libs/img/chesspieces/wikipedia/{piece}.png"
        else:
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
                    print(f"Warning: Square {square_id} not found in the DOM. Ensure it exists.")
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

        # ID der Quelle auslesen
        source_square_id = event.dataTransfer.getData("text")
        target_element = event.target

        # Debugging: Ziel-Element anzeigen
        print(f"Event target: {target_element}, ID: {getattr(target_element, 'id', 'None')}")

        # Ziel-Element oder Eltern-Element mit ID finden
        while not hasattr(target_element, "id") or not target_element.id:
            target_element = target_element.parentElement
            if not target_element:  # Fallback, falls kein Elternteil mit ID gefunden wird
                print("Error: Could not find a valid target element with an ID.")
                return

        target_square_id = target_element.id

        # Validierung der IDs
        if not source_square_id or not target_square_id:
            print(f"Error: Invalid drag-and-drop data. Source: {source_square_id}, Target: {target_square_id}")
            return

        print(f"Source: {source_square_id}, Target: {target_square_id}")
        if source_square_id != target_square_id:
            try:
                start_row, start_col = int(source_square_id[0]), int(source_square_id[1])
                end_row, end_col = int(target_square_id[0]), int(target_square_id[1])
                
                global game_state
                
                if game_state.game_status != "running" and not game_state.both_joined:
                    print("Game has not started yet!")
                    return
                
                if not game_state.is_move_legal(start_row, start_col, end_row, end_col):
                    print("Illegal move attempted.")
                    return

                print(f"Moving piece from ({start_row}, {start_col}) to ({end_row}, {end_col})")
                source_square = document[source_square_id]
                if source_square and source_square.firstChild:
                    socket_handler.send_move((start_row, start_col), (end_row, end_col))
                else:
                    print(f"Error: No piece to move from {source_square_id}.")
            except ValueError:
                print("Error: Invalid square IDs.")


                
    @staticmethod
    def display_game_id(game_id):
        if "gameIdDisplay" not in document:
            print("Error: 'gameIdDisplay' not found in the DOM.")
            return
        print(f"'gameIdDisplay' found. Setting Game ID to: {game_id}")
        game_id_element = document["gameIdDisplay"]
        game_id_element.style.display = "block"
        game_id_element.text = f"Game ID: {game_id}"
        
    @staticmethod
    def debug_print_pieces():
        print("Current pieces on the board:")
        for row in range(8):
            for col in range(8):
                position = f"{row}{col}"
                square = document[position]
                print(position)
                print(square)
                if square:
                    print(square.children)
                    for child in square.children:
                        if child.Class == "piece":
                            print(f"Piece at {position}: {child.src}")






game_state = GameState()
socket_handler = WebSocketHandler(game_state)
EventBindings.bind_events()


def game_init(mode = None):
    UI.create_chessboard()
    UI.add_drag_and_drop()
    game_state.player_name = game_state.generate_player_name()
    if mode == "create":
        API.create_game(game_state)
    API.join_game(game_state, callback=lambda: (
    socket_handler.connect(),
    UI.display_game_id(game_state.game_id)
    ))
    UI.update_board_state(game_state.board_state)
    
    
