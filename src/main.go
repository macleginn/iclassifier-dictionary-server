package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strconv"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type Empty struct{}

type FullDictEntry struct {
	Id           int    `json:"id"`
	StringID     string `json:"string_id"`
	Entry        string `json:"entry"`
	ShortMeaning string `json:"short_meaning"`
	Meaning      string `json:"meaning"`
	Examples     string `json:"examples"`
	Comments     string `json:"comments"`
}

type SmallDictEntry struct {
	Entry        string `json:"entry"`
	ShortMeaning string `json:"short_meaning"`
}

var supportedLanguages = map[string]struct{}{
	"tla":     Empty{},
	"chinese": Empty{},
}

func unboxNullString(s sql.NullString) string {
	if s.Valid {
		return s.String
	} else {
		return ""
	}
}

func getRecordById(id int, language string) (FullDictEntry, error) {
	var stringID string
	var entry string
	var shortMeaning sql.NullString
	var shortMeaningResult string
	var meaning sql.NullString
	var meaningResult string
	var examples sql.NullString
	var examplesResult string
	var comments sql.NullString
	var commentsResult string

	row := db.QueryRow(
		"SELECT entry,`short_meaning`,meaning,examples,comments FROM "+language+" WHERE id = ?",
		id)
	err := row.Scan(&entry, &shortMeaning, &meaning, &examples, &comments)
	if err == sql.ErrNoRows {
		return FullDictEntry{}, err
	}

	shortMeaningResult = unboxNullString(shortMeaning)
	meaningResult = unboxNullString(meaning)
	examplesResult = unboxNullString(examples)
	commentsResult = unboxNullString(comments)

	fde := FullDictEntry{
		Id:           id,
		StringID:     stringID,
		Entry:        entry,
		ShortMeaning: shortMeaningResult,
		Meaning:      meaningResult,
		Examples:     examplesResult,
		Comments:     commentsResult}

	return fde, nil
}

func sanitize(s string) string {
	return strings.Replace(s, "'", "''", -1)
}

func runSubstringQuery(dictionary string, substring string, queryType string) string {
	var queryString string

	if queryType == "transliteration" {
		queryString = fmt.Sprintf(
			"SELECT id, entry, `short_meaning` FROM %s WHERE entry LIKE \"%%%s%%\"",
			dictionary,
			sanitize(substring))
	} else {
		queryString = fmt.Sprintf(
			"SELECT id, entry, `short_meaning` FROM %s WHERE `short_meaning` LIKE \"%%%s%%\"",
			dictionary,
			sanitize(substring))
	}
	fmt.Println(queryString)

	rows, err := db.Query(queryString)
	if err != nil {
		log.Fatal(err)
	}

	var id int
	var entry string
	var shortMeaning sql.NullString
	var shortMeaningResult string

	result := map[string]SmallDictEntry{}

	for rows.Next() {
		err = rows.Scan(
			&id,
			&entry,
			&shortMeaning)
		if err != nil {
			log.Fatal(err)
		}
		shortMeaningResult = unboxNullString(shortMeaning)
		result[strconv.Itoa(id)] = SmallDictEntry{Entry: entry, ShortMeaning: shortMeaningResult}
	}
	rows.Close()

	jsonString, err := json.Marshal(result)
	if err != nil {
		log.Fatal(err)
	}

	return string(jsonString)
}

func HandleByID(w http.ResponseWriter, req *http.Request, language string) {
	queryValues := req.URL.Query()
	w.Header().Set("Access-Control-Allow-Origin", "*")

	idString := queryValues.Get("id")
	if idString == "" {
		w.WriteHeader(http.StatusBadRequest)
		io.WriteString(w, "No id provided.")
		return
	}
	id, err := strconv.Atoi(idString)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		io.WriteString(w, fmt.Sprintf("Bad id: %s.", idString))
		return
	}

	queryResult, err := getRecordById(id, language)
	var result []byte
	if err == sql.ErrNoRows {
		result = []byte("{}")
	} else if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		io.WriteString(w, "")
		return
	} else {
		result, err = json.Marshal(queryResult)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			io.WriteString(w, "")
			return
		}
	}
	w.Header().Set("Access-Control-Allow-Origin", "*")
	io.WriteString(w, string(result))
}

func HandleBySubstring(w http.ResponseWriter, req *http.Request, language string) {
	queryValues := req.URL.Query()
	w.Header().Set("Access-Control-Allow-Origin", "*")

	if substring := queryValues.Get("substr"); substring == "" {
		w.WriteHeader(http.StatusBadRequest)
		io.WriteString(w, "No substring provided.")
		return
	} else {
		queryType := queryValues.Get("type")
		if queryType == "" {
			queryType = "transliteration"
		}
		if queryType != "transliteration" && queryType != "translation" {
			w.WriteHeader(http.StatusBadRequest)
			io.WriteString(w, "Wrong type: must be \"transliteration\" or \"translation\"")
			return
		}
		queryResult := runSubstringQuery(language, substring, queryType)
		w.Header().Set("Content-Type", "application/json")
		io.WriteString(w, queryResult)
	}
}

func HandleRequest(w http.ResponseWriter, req *http.Request) {
	path := strings.Trim(req.URL.Path, "/")
	fmt.Println(path)
	slashIdx := strings.Index(path, "/")
	if slashIdx < 0 {
		w.WriteHeader(http.StatusBadRequest)
		io.WriteString(w, fmt.Sprintf("Invalid URL suffix: %s", path))
		return
	}
	pathComponents := strings.Split(path, "/")

	// Check language
	language := pathComponents[0]
	if _, ok := supportedLanguages[language]; !ok {
		w.WriteHeader(http.StatusBadRequest)
		io.WriteString(w, fmt.Sprintf("Dictionary %s is not available.", language))
		return
	}

	// Dispatch request by type
	route := pathComponents[1]
	switch route {
	case "byid":
		HandleByID(w, req, language)
	case "bysubstring":
		HandleBySubstring(w, req, language)
	default:
		w.WriteHeader(http.StatusBadRequest)
		io.WriteString(w, fmt.Sprintf("Bad route: %s.", route))
		return
	}
}

func main() {
	var err error
	db, err = sql.Open("sqlite3", "data/dictionary.sqlite")
	if err != nil {
		log.Fatal(err)
	}
	http.HandleFunc("/", HandleRequest)
	log.Fatal(http.ListenAndServe(":30000", nil))
	defer db.Close()
}
