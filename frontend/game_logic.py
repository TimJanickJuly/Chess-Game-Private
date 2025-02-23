from browser import document, html, ajax, websocket, alert, window, bind
import json

class Config:
    BASE_URL = f"http://{window.location.hostname}:8000"
    WS_URL = f"ws://{window.location.hostname}:8000/ws"

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
        self.remaining_time = {}
        self.game_history = []

    def update_from_response(self, response):
        self.game_status = response.get("game_state", self.game_status)
        self.num_moves_played = response.get("num_moves_played", self.num_moves_played)
        self.active_player = response.get("active_player", self.active_player)
        self.players = response.get("players", self.players)
        self.player_colors = response.get("player_colors", self.player_colors)
        self.both_joined = response.get("both_joined", self.both_joined)
        self.board_state = response.get("board_state", self.board_state)
        self.remaining_time = response.get("remaining_time", self.remaining_time)
        self.game_history = response.get("game_history", self.game_history)
        legal_moves_resp = response.get("legal_moves", self.legal_moves)
        self.legal_moves = legal_moves_resp["legal_moves"].get(self.player_name, [])
        if not self.own_color:
            self.own_color = self.player_colors.get(self.player_name, None)
        if not self.both_joined:
            self.text = "Waiting for Opponent"
        else:
            self.text = f"It's {self.player_colors[self.active_player]}'s turn!"
        if response.get('game_state', None) in ['black wins', 'white wins', 'stalemate']:
            self.text = response.get('game_state', None)
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
            for piece_type, start_square, end_squares in self.legal_moves:
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
            self.socket = websocket.WebSocket(f"{Config.WS_URL}/{self.game_state.game_id}/{self.game_state.player_name}")
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
            if data.get("event") in ["state", "update"]:
                state = data.get("state", {})
                if not state:
                    print("Invalid state data received.")
                    return
                print("Received new game state:", state)
                self.game_state.update_from_response(state)
                UI.update_board_state(self.game_state.board_state)
                UI.update_game_state(self.game_state.text)
            elif data.get("event") == "error":
                print(f"Error from server: {data.get('detail')}")
            else:
                print(f"Unhandled event type: {data.get('event')}")
        except json.JSONDecodeError:
            print("Failed to parse WebSocket message.")
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")

    def on_close(self, event):
        self.socket_open = False
        print("WebSocket disconnected. Attempting to reconnect in 5 seconds...")
        window.setTimeout(self.connect, 5000)

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
            return

        try:
            move_data = {
                "action": "move",
                "move": {
                    "move_type": "coordinates",
                    "start_row": start[0],
                    "start_col": start[1],
                    "target_row": end[0],
                    "target_col": end[1]
                }
            }
            self.socket.send(json.dumps(move_data))
            print("Move successfully sent.")
        except Exception as e:
            print(f"Failed to send move: {e}")

class API:
    @staticmethod
    def get_game_info(game_state, callback):
        url = Config.BASE_URL + f"/game_info/{game_state.game_id}/{game_state.player_name}"
        def handle_response(response):
            if response.status == 200:
                try:
                    info = json.loads(response.text)
                    callback(info)
                except Exception as e:
                    print(f"Error processing game info: {e}")
            else:
                print(f"Error: HTTP {response.status}")
        ajax.get(url, oncomplete=handle_response)
        
    def can_i_join(game_id, callback):
        if not game_state.player_name:
            game_state.player_name = game_state.generate_player_name()
        url = Config.BASE_URL + f"/game_info/{game_id}/{game_state.player_name}"
        print(f"Asking whether I can join: {url}")
        def handle_response(response):
            if response.status == 200:
                try:
                    game_info = json.loads(response.text)
                    print("Game info received:", game_info)
                    joinable = not game_info.get("both_joined", False)
                    callback(joinable)
                except Exception as e:
                    print(f"Error processing game info: {e}")
                    callback(False)
            else:
                print(f"Error: HTTP {response.status}")
                callback(False)
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
        if event.keyCode == 13:
            input_field = document["gameIdInput"]
            if not input_field:
                print("Error: 'gameIdInput' not found in the DOM.")
                return
            game_id = input_field.value.strip()
            print("Trying to join: ", game_id)
            if game_id:
                if not game_state.player_name:
                    game_state.player_name = game_state.generate_player_name()
                def handle_can_i_join_response(joinable):
                    if joinable:
                        print(f"Game ID entered: {game_id}")
                        game_state.game_id = game_id
                        game_init()
                    else:
                        alert("Game is full or cannot be joined.")
                API.can_i_join(game_id, callback=handle_can_i_join_response)
            else:
                alert("Please enter a valid Game ID!")

class UI:
    timer_interval_id = None
    last_timer_update = None
    timeout_checked = False
    timer_stopped = False

    @staticmethod
    def ensure_remaining_time_display():
        container = document.getElementById("remainingTimeDisplay")
        if not container:
            container = html.DIV(Id="remainingTimeDisplay")
            container.style.position = "absolute"
            container.style.top = "50px"
            container.style.right = "50px"
            container.style.padding = "10px"
            container.style.border = "1px solid #ccc"
            container.style.backgroundColor = "#666"
            document <= container

    @staticmethod
    def update_remaining_time_display():
        container = document.getElementById("remainingTimeDisplay")
        if container:
            text = "Remaining Time:\n"
            active_color = game_state.player_colors.get(game_state.active_player, None)
            for color, time in game_state.remaining_time.items():
                if color == active_color:
                    text += f"{color} (active): {time:.1f} s\n"
                else:
                    text += f"{color}: {time:.1f} s\n"
            container.text = text

    @staticmethod
    def start_timer():
        if UI.timer_interval_id is None:
            UI.last_timer_update = window.performance.now()
            UI.timer_interval_id = window.setInterval(UI.tick_timer, 1000)

    @staticmethod
    def stop_timer():
        if UI.timer_interval_id is not None:
            window.clearInterval(UI.timer_interval_id)
            UI.timer_interval_id = None
        UI.timer_stopped = True

    @staticmethod
    def tick_timer():
        if UI.timer_stopped:
            return
        now = window.performance.now()
        elapsed = (now - UI.last_timer_update) / 1000.0
        UI.last_timer_update = now
        if game_state.remaining_time and game_state.player_colors:
            active_color = game_state.player_colors.get(game_state.active_player)
            if active_color in game_state.remaining_time:
                game_state.remaining_time[active_color] = max(0, game_state.remaining_time[active_color] - elapsed)
        UI.update_remaining_time_display()
        for color, time_left in game_state.remaining_time.items():
            if time_left <= 0 and not UI.timeout_checked:
                UI.timeout_checked = True
                print(f"Timeout for {color}. Requesting updated game info...")
                API.get_game_info(game_state, callback=UI.handle_timeout_response)
                break

    @staticmethod
    def handle_timeout_response(info):
        game_state.update_from_response(info)
        for color, time_left in game_state.remaining_time.items():
            if time_left <= 0:
                winner = "white wins" if color == "black" else "black wins"
                game_state.text = winner
                UI.update_game_state(winner)
                UI.stop_timer()
                break

    @staticmethod
    def create_game_area():
        board = document["board"]
        board_parent = board.parentElement
        game_area = html.DIV(Id="gameArea")
        game_area.style.display = "flex"
        game_area.style.justifyContent = "center"
        game_area.style.alignItems = "flex-start"
        board.style.display = "grid"
        board.style.gridTemplateRows = board.style.gridTemplateColumns = "repeat(8, 60px)"
        game_area <= board
        history_container = UI.create_game_history_container()
        if history_container:
            game_area <= history_container
        board_parent <= game_area

    @staticmethod
    def create_chessboard():
        board = document["board"]
        if not board:
            print("Error: Chessboard container not found in the DOM.")
            return
        colors = ["white", "black"]
        board.clear()
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                square = html.DIV(Class=f"square {color}", Id=f"{row}{col}")
                board <= square
        for btn_id in ["createGameBtn", "showInputBtn", "gameIdInput"]:
            element = document[btn_id]
            if element:
                element.style.display = "none"
            else:
                print(f"Warning: Element '{btn_id}' not found in the DOM.")
        UI.ensure_remaining_time_display()
        UI.start_timer()
        UI.create_game_area()

    @staticmethod
    def create_game_history_container():
        if "gameHistoryContainer" in document:
            return
        container = html.DIV(Id="gameHistoryContainer")
        container.style.display = "inline-block"
        container.style.verticalAlign = "top"
        container.style.marginLeft = "20px"
        container.style.width = "200px"
        container.style.border = "1px solid #ccc"
        container.style.backgroundColor = "#666"
        container.style.padding = "10px"
        container.style.fontSize = "16px"
        container.style.fontFamily = "Arial, sans-serif"
        header = html.H3("Game History")
        header.style.marginTop = "0"
        container <= header
        table = html.TABLE(Id="gameHistoryTable")
        table.style.width = "100%"
        container <= table
        return container

    @staticmethod
    def update_game_history():
        if "gameHistoryContainer" not in document:
            return
        container = document["gameHistoryContainer"]
        table = document["gameHistoryTable"]
        while table.firstChild:
            table.removeChild(table.firstChild)
        for entry in game_state.game_history:
            move_number = entry[0]
            moves = entry[1]
            row = html.TR()
            move_num_cell = html.TD(f"{move_number}.")
            move_num_cell.style.width = "30px"
            row <= move_num_cell
            white_move = moves[0] if len(moves) > 0 else ""
            black_move = moves[1] if len(moves) > 1 else ""
            moves_cell = html.TD(f"{white_move} {black_move}")
            row <= moves_cell
            table <= row
        def compute_font_size(num_moves):
            max_size = 16
            min_size = 8
            threshold = 15
            if num_moves <= threshold:
                return max_size
            new_size = max(max_size - (num_moves - threshold) * 0.4, min_size)
            return new_size
        new_font_size = compute_font_size(len(game_state.game_history))
        container.style.fontSize = f"{new_font_size}px"

    @staticmethod
    def update_game_state(new_state):
        game_state_element = document["gameState"]
        if game_state_element:
            game_state_element.innerText = new_state
        else:
            print("Error: 'gameState' element not found in the DOM.")

    @staticmethod
    def place_piece(row, col, piece):
        position = f"{row}{col}"
        square = document[position]
        if not square:
            print(f"Error: Square {position} not found in the DOM.")
            return
        def has_piece(sq):
            for child in sq.children:
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
        board = document["board"]
        board.classList.add("board-update")
        window.setTimeout(lambda: board.classList.remove("board-update"), 1000)
        if not board_state or len(board_state) != 8 or any(len(row) != 8 for row in board_state):
            print("Error: Invalid board_state provided.")
            return
        flipped = game_state.own_color == "black"
        for row in range(8):
            for col in range(8):
                if flipped:
                    display_row = 7 - row
                    display_col = 7 - col
                else:
                    display_row = row
                    display_col = col
                piece = game_state.piece_encoding.get(board_state[row][col])
                if piece is None and board_state[row][col] != 0:
                    print(f"Warning: Unrecognized piece code at ({row}, {col}).")
                UI.place_piece(display_row, display_col, piece)
        UI.update_remaining_time_display()
        UI.update_game_history()


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
        event.preventDefault()

    @staticmethod
    def drag_start(event):
        parent_id = event.target.parent.id if event.target.parent else None
        if parent_id:
            event.dataTransfer.setData("text", parent_id)
        else:
            print("Warning: drag_start failed due to missing parent ID.")

    @staticmethod
    def drop(event):
        event.preventDefault()
        source_square_id = event.dataTransfer.getData("text")
        target_element = event.target
        while not hasattr(target_element, "id") or not target_element.id:
            target_element = target_element.parentElement
            if not target_element:
                print("Error: Could not find a valid target element with an ID.")
                return
        target_square_id = target_element.id
        if not source_square_id or not target_square_id:
            print(f"Error: Invalid drag-and-drop data. Source: {source_square_id}, Target: {target_square_id}")
            return
        try:
            start_row, start_col = int(source_square_id[0]), int(source_square_id[1])
            end_row, end_col = int(target_square_id[0]), int(target_square_id[1])
            global game_state
            flipped = game_state.own_color == "black"
            if flipped:
                start_row, start_col = 7 - start_row, 7 - start_col
                end_row, end_col = 7 - end_row, 7 - end_col
            if game_state.game_status != "running" and not game_state.both_joined:
                print("Game has not started yet!")
                return
            if not game_state.is_move_legal(start_row, start_col, end_row, end_col):
                print("Illegal move attempted.")
                return
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
        game_id_element = document["gameIdDisplay"]
        game_id_element.style.display = "block"
        game_id_element.text = f"Game ID: {game_id}"

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
