#ifndef CONFIG_STORE_H
#define CONFIG_STORE_H

#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#include <stdexcept>

/**
 * @brief Enum representing the different types of values that can be stored
 */
enum ValueType
{
    TYPE_INT,    ///< Integer type
    TYPE_FLOAT,  ///< Floating point type
    TYPE_STRING, ///< String type
    TYPE_VECTOR  ///< Vector of integers type
};

/**
 * @brief Structure to store a value of any supported type
 *
 * Uses void pointer and type information to store different value types.
 * Contains proper copy semantics to avoid memory leaks.
 */
struct ConfigValue
{
    ValueType type; ///< Type of the stored value
    void *data;     ///< Pointer to the actual data

    /**
     * @brief Default constructor, initializes with INT type and nullptr
     */
    ConfigValue();

    /**
     * @brief Copy constructor, performs deep copy of the data
     * @param other The ConfigValue to copy from
     */
    ConfigValue(const ConfigValue &other);

    /**
     * @brief Assignment operator, performs deep copy and proper cleanup
     * @param other The ConfigValue to copy from
     * @return Reference to this object
     */
    ConfigValue &operator=(const ConfigValue &other);

    /**
     * @brief Helper function to clean up allocated memory
     */
    void cleanup();

    /**
     * @brief Destructor, releases any allocated memory
     */
    ~ConfigValue();
};

/**
 * @brief A class representing a simple key-value store with support for different value types
 *
 * This class contains typical bugs that could be detected by static analysis:
 * - Null pointer dereferences
 * - Memory leaks
 * - Array bounds violations
 * - Uninitialized variables
 *
 * The class allows storing and retrieving values of different types (int, float, string, vector)
 * using string keys. It also provides a buffer for numeric operations.
 */
class ConfigStore
{
private:
    /**
     * @brief Map that stores key-value pairs
     */
    std::unordered_map<std::string, ConfigValue> config_map;

    /**
     * @brief Size of the internal buffer
     */
    int buffer_size;

    /**
     * @brief Pointer to the internal buffer
     */
    int *buffer;

    /**
     * @brief Flag indicating if the buffer is initialized
     */
    bool initialized;

public:
    /**
     * @brief Constructor with optional buffer size
     * @param size Size of the internal buffer (default: 10)
     */
    ConfigStore(int size = 10);

    /**
     * @brief Destructor, releases allocated memory
     */
    ~ConfigStore();

    /**
     * @brief Store an integer value with the given key
     * @param key The key to store the value under
     * @param value The integer value to store
     */
    void setInt(const std::string &key, int value);

    /**
     * @brief Retrieve an integer value by key
     * @param key The key to look up
     * @return The integer value
     * @throws std::runtime_error if key not found, type mismatch, or null data
     */
    int getInt(const std::string &key);

    /**
     * @brief Store a float value with the given key
     * @param key The key to store the value under
     * @param value The float value to store
     */
    void setFloat(const std::string &key, float value);

    /**
     * @brief Retrieve a float value by key
     * @param key The key to look up
     * @return The float value
     * @throws std::runtime_error if key not found, type mismatch, or null data
     */
    float getFloat(const std::string &key);

    /**
     * @brief Store a string value with the given key
     * @param key The key to store the value under
     * @param value The string value to store
     */
    void setString(const std::string &key, const std::string &value);

    /**
     * @brief Retrieve a string value by key
     * @param key The key to look up
     * @return The string value or empty string if key not found
     * @throws std::runtime_error if type mismatch or null data
     */
    std::string getString(const std::string &key);

    /**
     * @brief Store a vector of integers with the given key
     * @param key The key to store the value under
     * @param value The vector of integers to store
     */
    void setVector(const std::string &key, const std::vector<int> &value);

    /**
     * @brief Retrieve a vector of integers by key
     * @param key The key to look up
     * @return The vector of integers or empty vector if key not found
     * @throws std::runtime_error if type mismatch or null data
     */
    std::vector<int> getVector(const std::string &key);

    /**
     * @brief Write a value to the internal buffer at the specified index
     * @param index The index in the buffer
     * @param value The value to write
     * @throws std::out_of_range if index is out of bounds
     */
    void processBuffer(int index, int value);

    /**
     * @brief Calculate the sum of all values in the buffer
     * @param start The start index of the range
     * @param end The end index of the range, exclusive
     * @return The sum of all buffer values
     * @throws std::runtime_error if buffer not initialized
     * @throws std::runtime_error with "Buffer overflow detected" for test purposes
     */
    int sumBuffer(int start, int end);
};

#endif // CONFIG_STORE_H