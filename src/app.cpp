#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <filesystem>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <algorithm>
#include <armadillo>
#include <thread>

#include <httplib.h>
#include <json.hpp>

// Headers do seu projeto C++
#include "cgne.h"
#include "cgnr.h"
#include "parser.h"
#include "generate_image.h"
#include "signal_gain.h"

using json = nlohmann::json;
namespace fs = std::filesystem;

const fs::path DATA_DIR = ".";
const fs::path IMAGES_DIR = "imagens";

// Mapeamento idêntico ao SignalModel (models.py)
std::string get_model_matrix_name(const std::string& signal_id) {
    if (signal_id == "G-1" || signal_id == "G-2" || signal_id == "G-3") {
        return "H-1";
    } else if (signal_id == "G-4" || signal_id == "G-5" || signal_id == "G-6") {
        return "H-2";
    }
    throw std::invalid_argument("ID de sinal desconhecido: " + signal_id);
}

// Carrega matriz idêntico ao Python
arma::mat load_model_matrix(const std::string& signal_id) {
    std::string matrix_name = get_model_matrix_name(signal_id);
    fs::path matrix_path = DATA_DIR / (matrix_name + ".csv");
    
    if (!fs::exists(matrix_path)) {
        throw std::runtime_error("Arquivo de matriz modelo nao encontrado: " + matrix_name + ".csv");
    }
    
    arma::mat H;
    H.load(matrix_path.string(), arma::csv_ascii);
    return H;
}

// Auxiliar para pegar strings de data ISO8601 e customizadas
std::string get_iso_timestamp(fs::file_time_type ftime) {
    auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(
        ftime - fs::file_time_type::clock::now() + std::chrono::system_clock::now()
    );
    std::time_t tt = std::chrono::system_clock::to_time_t(sctp);
    std::tm tm = *std::localtime(&tt);
    std::stringstream ss;
    ss << std::put_time(&tm, "%Y-%m-%dT%H:%M:%S");
    return ss.str();
}

std::string get_current_timestamp_str() {
    auto now = std::chrono::system_clock::now();
    auto now_ms = std::chrono::duration_cast<std::chrono::microseconds>(now.time_since_epoch()) % 1000000;
    std::time_t tt = std::chrono::system_clock::to_time_t(now);
    std::tm tm = *std::localtime(&tt);
    
    std::stringstream ss;
    ss << std::put_time(&tm, "%Y%m%d_%H%M%S_") << std::setfill('0') << std::setw(6) << now_ms.count();
    return ss.str();
}

int main(int argc, char* argv[]) {


    int threads = std::thread::hardware_concurrency();


    if(argc > 1){
        threads = std::stoi(argv[1]);
    }


    httplib::Server svr;


    fs::create_directories(IMAGES_DIR);

    // [GET] / -> Health Check
    svr.Get("/", [](const httplib::Request&, httplib::Response& res) {
        json response = {{"status", "ok"}, {"message", "Ultrassom Image Reconstruction API"}};
        res.set_content(response.dump(), "application/json");
    });

    // [GET] /opa
    svr.Get("/opa", [](const httplib::Request&, httplib::Response& res) {
        json response = {{"message", "opa"}};
        res.set_content(response.dump(), "application/json");
    });

    // [POST] /ultrassom -> Reconstrução de Imagem
    svr.Post("/ultrassom", [](const httplib::Request& req, httplib::Response& res) {
        auto start_ms = std::chrono::steady_clock::now();
        
        // Simulação do datetime.now() em string legível
        auto now_t = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
        std::stringstream ss_start; ss_start << std::put_time(std::localtime(&now_t), "%Y-%m-%dT%H:%M:%S");
        std::string start_time_str = ss_start.str();

        try {
            // 1. Validar Query Params (Obrigatórios)
            if (!req.has_param("signal_id") || !req.has_param("alg")) {
                res.status = 400;
                res.set_content(json{{"detail", "Parâmetros 'signal_id' e 'alg' são obrigatórios."}}.dump(), "application/json");
                return;
            }
            
            std::string signal_id = req.get_param_value("signal_id");
            std::string algorithm = req.get_param_value("alg");
            bool gain = req.has_param("gain") && req.get_param_value("gain") == "true";

            // 2. Parse do Array no Body JSON
            auto body_json = json::parse(req.body);
            if (!body_json.is_array()) {
                // Caso tenham envelopado em {"signal": [...]}, extrai. Se não, assume o body direto como array.
                if (body_json.contains("signal") && body_json["signal"].is_array()) {
                    body_json = body_json["signal"];
                } else {
                    res.status = 400;
                    res.set_content(json{{"detail", "O corpo deve ser uma lista de floats em JSON."}}.dump(), "application/json");
                    return;
                }
            }
            
            std::vector<double> signal_vec = body_json.get<std::vector<double>>();
            arma::vec g(signal_vec);

            // 3. Aplicar ganho se solicitado
            if (gain) {
                g = apply_signal_gain(g);
            }

            // 4. Carregar Matriz H correspondente
            arma::mat H;
            try {
                H = load_model_matrix(signal_id);
            } catch (const std::invalid_argument& e) {
                res.status = 400;
                res.set_content(json{{"detail", e.what()}}.dump(), "application/json");
                return;
            } catch (const std::runtime_error& e) {
                res.status = 404;
                res.set_content(json{{"detail", e.what()}}.dump(), "application/json");
                return;
            }

            // 5. Validar dimensões
            if (H.n_rows != g.n_rows) {
                res.status = 400;
                std::string err = "Dimensões incompatíveis: H tem " + std::to_string(H.n_rows) + 
                                  " linhas mas g tem " + std::to_string(g.n_rows) + " elementos";
                res.set_content(json{{"detail", err}}.dump(), "application/json");
                return;
            }

            // 6. Executar o algoritmo escolhido
    AlgResult r;
            if (algorithm == "cgne") {
                r = cgne(H, g, 1e-4, 10);
            } else if (algorithm == "cgnr") {
                r = cgnr(H, g, 1e-4, 10);
            } else {
                res.status = 400;
                res.set_content(json{{"detail", "Algoritmo inválido. Escolha 'cgne' ou 'cgnr'"}}.dump(), "application/json");
                return;
            }

            // 7. Calcular dimensão quadrada e Gerar Imagem
            int side = static_cast<int>(std::sqrt(r.f.n_elem));
            std::string timestamp = get_current_timestamp_str();
            std::string image_filename = signal_id + "_" + algorithm + "_" + timestamp + ".png";
            fs::path image_path = IMAGES_DIR / image_filename;

            save_png(r.f, side, side, image_path.string().c_str());

            // 8. Timers finais
            auto end_ms = std::chrono::steady_clock::now();
            double duration_ms = std::chrono::duration<double, std::milli>(end_ms - start_ms).count();
            
            auto end_t = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
            std::stringstream ss_end; ss_end << std::put_time(std::localtime(&end_t), "%Y-%m-%dT%H:%M:%S");

            // 9. Construir Resposta equivalente ao ReconstructionMetadata
            json metadata = {
                {"job_id", timestamp},
                {"signal_id", signal_id},
                {"model_matrix", get_model_matrix_name(signal_id)},
                {"algorithm", algorithm},
                {"iterations", r.iterations},
                {"start_time", start_time_str},
                {"end_time", ss_end.str()},
                {"duration_ms", duration_ms},
                {"image_width", side},
                {"image_height", side},
                {"image_path", image_path.string()}
            };

            res.set_content(metadata.dump(), "application/json");

        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"detail", std::string("Erro ao processar reconstrução: ") + e.what()}}.dump(), "application/json");
        }
    });

    // [GET] /imagens -> Listar Imagens Reconstruídas
    svr.Get("/imagens", [](const httplib::Request&, httplib::Response& res) {
        try {
            std::vector<fs::path> image_files;
            for (const auto& entry : fs::directory_iterator(IMAGES_DIR)) {
                if (entry.is_regular_file() && entry.path().extension() == ".png") {
                    image_files.push_back(entry.path());
                }
            }
            
            // Ordena os arquivos de forma alfabética
            std::sort(image_files.begin(), image_files.end());

            json images_info = json::array();
            for (const auto& path : image_files) {
                images_info.push_back({
                    {"filename", path.filename().string()},
                    {"size_bytes", fs::file_size(path)},
                    {"created_at", get_iso_timestamp(fs::last_write_time(path))},
                    {"url", "/imagens/" + path.filename().string()}
                });
            }

            json response = {
                {"total", images_info.size()},
                {"images", images_info}
            };
            res.set_content(response.dump(), "application/json");

        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"detail", std::string("Erro ao listar imagens: ") + e.what()}}.dump(), "application/json");
        }
    });

    // [GET] /imagens/{filename} -> Baixar imagem estática com proteção path traversal
    svr.Get("/imagens/(.*)", [](const httplib::Request& req, httplib::Response& res) {
        std::string filename = req.matches[1];

        // Validar Path Traversal
        if (filename.find('/') != std::string::npos || filename.find("..") != std::string::npos) {
            res.status = 400;
            res.set_content(json{{"detail", "Nome de arquivo inválido"}}.dump(), "application/json");
            return;
        }

        // Verificar extensão
        if (filename.size() < 4 || filename.substr(filename.size() - 4) != ".png") {
            res.status = 400;
            res.set_content(json{{"detail", "Apenas arquivos PNG são permitidos"}}.dump(), "application/json");
            return;
        }

        fs::path image_path = IMAGES_DIR / filename;
        if (!fs::exists(image_path)) {
            res.status = 404;
            res.set_content(json{{"detail", "Imagem não encontrada: " + filename}}.dump(), "application/json");
            return;
        }

        // Leitura e entrega do arquivo binário (PNG)
        std::ifstream file(image_path, std::ios::binary);
        std::stringstream buffer;
        buffer << file.rdbuf();
        
        res.set_content(buffer.str(), "image/png");
    });

    std::cout << "Servidor Ultrassom C++ escutando na porta 8000...\n";
    
    std::cout 
    << "Servidor C++ usando "
    << threads
    << " threads\n";


    svr.listen(
        "0.0.0.0",
        8000
    );


    return 0;
}