from ctypes import *
import faulthandler

# Load the shared library into ctypes
libname = "./FFI/librealm-ffi-dbg.dylib"
realm_ffi = cdll.LoadLibrary(libname)

# /classes and properties for testing

# define class info
# typedef struct realm_class_info {
#     const char* name;
#     const char* primary_key;
#     size_t num_properties;
#     size_t num_computed_properties;
#     realm_class_key_t key;
#     int flags;
# } realm_class_info_t;


class Class_Info(Structure):
    _fields_ = [
        ("name", c_char_p),
        ("primary_key", c_char_p),
        ("num_properties", c_longlong),
        ("num_computed_properties", c_longlong),
        ("key", c_int),
        ("flags", c_longlong),
    ]


# define property info
# typedef struct realm_property_info {
#     const char* name;
#     const char* public_name;
#     realm_property_type_e type;
#     realm_collection_type_e collection_type;
#     const char* link_target;
#     const char* link_origin_property_name;
#     realm_property_key_t key;
#     int flags;
# } realm_property_info_t;
class Property_Info(Structure):
    _fields_ = [
        ("name", c_char_p),
        ("public_name", c_char_p),
        ("type", c_int),
        ("collection_type", c_int),
        ("link_target", c_char_p),
        ("link_origin_property_name", c_char_p),
        ("key", c_int),
        ("flags", c_longlong),
    ]


# here we can pack our structs from our cdll into a buffer
def buffer_pack_bytes(instance):
    buffer = string_at(byref(instance), sizeof(instance))
    return buffer


# we can cast our string with pointer to the string we want
def buffer_unpack_bytes(ctype, buffer):
    cstring = create_string_buffer(buffer)
    instance = cast(pointer(cstring), POINTER(ctype)).contents
    return instance


# /end of classes and properties


# define error check for last error
# typedef struct realm_error {
#     realm_errno_e error;
#     const char* message;
#     // When error is RLM_ERR_CALLBACK this is an opaque pointer to an SDK-owned error object
#     // thrown by user code inside a callback with realm_register_user_code_callback_error(), otherwise null.
#     void* usercode_error;
#     union {
#         int code;
#         realm_logic_error_kind_e logic_error_kind;
#     } kind;
# } realm_error_t;
class Error(Structure):
    _fields_ = [
        ("error", c_int),
        ("message", c_char_p),
        ("usercode_error", c_char_p),
        ("kind", c_int),
    ]


def check_error():
    err = Error()
    realm_ffi.realm_get_last_error.argtypes = [POINTER(Error)]
    realm_ffi.realm_get_last_error(byref(err))
    print(err.message)


class Get_class_keys(Structure):
    _fields_ = [("out_keys", c_void_p), ("out_n", c_void_p)]


def array_buffer_int32_bit(struct, field):
    ArrayType = c_int32 * 2000
    in_data = struct
    data_buffer = ArrayType()
    in_data.field = c_void_p(addressof(data_buffer))  # or cast(data_buffer, c_void_p)


class Realm_Find_Class(Structure):
    _fields_ = [("out_found", c_bool), ("out_class_info", c_void_p)]

    def get_found():
        return _fields_[0]


def array_buffer_string(struct, field):
    ArrayType = c_char * 2000
    in_data = struct
    data_buffer = ArrayType()
    in_data.field = c_void_p(addressof(data_buffer))  # or cast(data_buffer, c_void_p)


def array_buffer_schema(struct):
    ArrayType = c_void_p * 2000
    in_data = struct
    data_buffer = ArrayType()
    in_data = c_void_p(addressof(data_buffer))


# define schema
# /**
#  * Create a new schema from classes and their properties.
#  *
#  * Note: This function does not validate the schema.
#  *
#  * Note: `realm_class_key_t` and `realm_property_key_t` values inside
#  *       `realm_class_info_t` and `realm_property_info_t` are unused when
#  *       defining the schema. Call `realm_get_schema()` to obtain the values for
#  *       these fields in an open realm.
#  *
#  * @return True if allocation of the schema structure succeeded.
#  */
# RLM_API realm_schema_t* realm_schema_new(const realm_class_info_t* classes, size_t num_classes,
#                                          const realm_property_info_t** class_properties);


class Schema:
    def wrap(self, a):  # this will break when using more than 1 class
        x = len(a)
        y = len(a[0])
        arr = (
            POINTER(Property_Info) * x
        )()  # allocate array of pointers in X dimension
        for i in range(x):
            arr[i] = (Property_Info * y)(
                *a[i]
            )  # allocate array in Y dimension and populate it
        return arr, x, y

    def __init__(self):
        sample_classes = [
            Class_Info("TodoItem".encode("utf-8"), "".encode("utf-8"), 3, 0, 0, 0)
        ]
        sample_classes_ptr = (Class_Info * 1)(*sample_classes)  # only 1 class atm

        realm_ffi.realm_schema_new.restype = c_void_p

        realm_ffi.realm_schema_new.argtypes = [
            POINTER(Class_Info),
            c_size_t,
            POINTER(POINTER(Property_Info)),
        ]

        class_properties = [
            [
                Property_Info(
                    "foo".encode("utf-8"),
                    "_foo".encode("utf-8"),
                    0,
                    0,
                    "".encode("utf-8"),
                    "".encode("utf-8"),
                    0,
                    0,
                ),
                Property_Info(
                    "soo".encode("utf-8"),
                    "_soo".encode("utf-8"),
                    0,
                    0,
                    "".encode("utf-8"),
                    "".encode("utf-8"),
                    0,
                    0,
                ),
                Property_Info(
                    "doo".encode("utf-8"),
                    "_doo".encode("utf-8"),
                    0,
                    0,
                    "".encode("utf-8"),
                    "".encode("utf-8"),
                    0,
                    0,
                ),
            ]
        ]

        self.handle = c_void_p(
            realm_ffi.realm_schema_new(
                sample_classes_ptr, 1, *self.wrap(class_properties)
            )
        )
        check_error()
        print(self.handle)
        print("ok")


# define configuration
# /**
#  * Allocate a new configuration with default options.
#  */
# RLM_API realm_config_t* realm_config_new(void);
class Configuration:
    def __init__(self, schema):
        realm_ffi.realm_config_new.restype = c_void_p
        self.handle = realm_ffi.realm_config_new()

        set_schema_version(c_void_p(self.handle))
        set_schema_object(c_void_p(self.handle), schema.handle)

        encoded_file = "gary.realm".encode("utf-8")
        set_path_for_realm(c_void_p(self.handle), c_char_p(encoded_file))
        print(self.handle)


# set schema object for realm
# /**
#  * Set the schema object for this realm.
#  *
#  * This does not take ownership of the schema object, and it should be released
#  * afterwards.
#  *
#  * This function aborts when out of memory, but otherwise cannot fail.
#  *
#  * @param schema The schema object. May be NULL, which means an empty schema.
#  */
# RLM_API void realm_config_set_schema(realm_config_t*, const realm_schema_t* schema);
def set_schema_object(handle, schema):
    realm_ffi.realm_config_set_schema.restype = c_void_p
    realm_ffi.realm_config_set_schema(handle, schema)


# #set schema version for realm
# /**
#  * Set the schema version of the schema.
#  *
#  * This function cannot fail.
#  */
# RLM_API void realm_config_set_schema_version(realm_config_t*, uint64_t version);
def set_schema_version(handle):
    realm_ffi.realm_config_set_schema_version.restype = c_void_p
    realm_ffi.realm_config_set_schema_version(handle, 1)


# define path for realm file
# /**
#  * Set the path of the realm being opened.
#  *
#  * This function aborts when out of memory, but otherwise cannot fail.
#  */
# RLM_API void realm_config_set_path(realm_config_t*, const char* path);
def set_path_for_realm(handle, encoded_file):
    realm_ffi.realm_config_set_path.restype = c_void_p
    realm_ffi.realm_config_set_path(handle, encoded_file)


# define our realm
class Realm:
    def __init__(self, configuration):
        self.configuration = configuration

        # open the realm
        # /**
        #  * Open a Realm file.
        #  *
        #  * @param config Realm configuration. If the Realm is already opened on another
        #  *               thread, validate that the given configuration is compatible
        #  *               with the existing one.
        #  * @return If successful, the Realm object. Otherwise, NULL.
        #  */
        # RLM_API realm_t* realm_open(const realm_config_t* config);

        realm_ffi.realm_open.restype = c_void_p
        self.handle = realm_ffi.realm_open(c_void_p(self.configuration.handle))
        print(self.handle)

    # release realm pointer owned by caller
    # /**
    # * Free any Realm C Wrapper object.
    # *
    # * Note: Any pointer returned from a library function is owned by the caller.
    # *       The caller is responsible for calling `realm_release()`. The only
    # *       exception from this is C++ bridge functions that return `void*`, with
    # *       the prefix `_realm`.
    # *
    # * Note: C++ destructors are typically `noexcept`, so it is likely that an
    # *       exception will crash the process.
    # *
    # * @param ptr A pointer to a Realm C Wrapper object. May be NULL.
    # */
    # RLM_API void realm_release(void* ptr);
    def realm_release(self):
        realm_ffi.realm_release.restype = c_void_p
        realm_ffi.realm_release(c_void_p(self.configuration.handle))

    # begin write transaction
    # /**
    # * Begin a write transaction for the Realm file.
    # *
    # * @return True if no exception occurred.
    # */
    # RLM_API bool realm_begin_write(realm_t*);
    def begin_write(self):
        Realm.begin_read(self.handle)
        assert realm_ffi.realm_begin_write(c_void_p(self.handle))
        # /**
        #  * Roll back a write transaction.
        #  *
        #  * @return True if the rollback succeeded and no exceptions were thrown.
        #  */
        # RLM_API bool realm_rollback(realm_t*);
        realm_ffi.realm_rollback.restype = c_bool
        assert realm_ffi.realm_rollback(c_void_p(self.handle))
        print("begin")

    # begin a read transaction
    # /**
    # * Begin a read transaction for the Realm file.
    # *
    # * @return True if no exception occurred.
    # */
    # RLM_API bool realm_begin_read(realm_t*);
    def begin_read(handle):
        realm_ffi.realm_begin_read.restype = c_bool
        realm_ffi.realm_begin_read(c_void_p(handle))

    # check if realm is closed
    # /**
    # * True if the Realm file is closed.
    # *
    # * This function cannot fail.
    # */
    # RLM_API bool realm_is_closed(realm_t*);
    def realm_is_closed(self):
        realm_ffi.realm_is_closed.restype = c_bool
        closed = realm_ffi.realm_is_closed(c_void_p(self.handle))
        if closed == False:
            print("The realm is not closed.")
        else:
            print("The realm is closed.")

    def realm_is_frozen(self):
        realm_ffi.realm_is_frozen.restype = c_bool
        frozen = realm_ffi.realm_is_frozen(c_void_p(self.handle))
        if frozen == False:
            print("The realm is not frozen.")
        else:
            print("The realm is frozen.")

    # check if realm is writeable
    # /**
    # * Return true if the realm is in a write transaction.
    # *
    # * This function cannot fail.
    # */
    # RLM_API bool realm_is_writable(const realm_t*);
    def realm_is_writable(self):
        realm_ffi.realm_is_writable.restype = c_bool
        succeed = realm_ffi.realm_is_writable(c_void_p(self.handle))
        if succeed == True:
            print("Realm is writeable")
        else:
            print("Realm is not writeable")

    #     /**
    #  * Return the number of classes in the Realm's schema.
    #  *
    #  * This cannot fail.
    #  */
    # RLM_API size_t realm_get_num_classes(const realm_t*);
    def realm_get_num_classes(self):
        realm_ffi.realm_get_num_classes.restype = c_int
        num_classes = realm_ffi.realm_get_num_classes(c_void_p(self.handle))
        print(num_classes)

    #     /**
    #  * Get the table keys for classes in the schema.
    #  * In case of errors this function will return false (errors to be fetched via `realm_get_last_error()`).
    #  * If data is not copied the function will return true and set  `out_n` with the capacity needed.
    #  * Data is only copied if the input array has enough capacity, otherwise the needed  array capacity will be set.
    #  *
    #  * @param out_keys An array that will contain the keys of each class in the
    #  *                 schema. Array may be NULL, in this case no data will be copied and `out_n` set if not NULL.
    #  * @param max The maximum number of keys to write to `out_keys`.
    #  * @param out_n The actual number of classes. May be NULL.
    #  * @return True if no exception occurred.
    #  */
    # RLM_API bool realm_get_class_keys(const realm_t*, realm_class_key_t* out_keys, size_t max, size_t* out_n);
    def realm_get_class_keys(self):
        realm_ffi.realm_get_class_keys.restype = c_bool
        out_keys = []
        out_n = 0
        # create buffer to hold out_keys, use realm_get_num_classes to set size of buffer
        # should be the same as how a string buffer works
        # buffer = ctypes.create_string_buffer(b"",realm_get_num_classes() * 4)
        # numpy
        # To get numpy array from the pointer, see How to convert pointer to c array to python array:

        # >>> import numpy
        # >>> pa = cast(in_data.pDataBuffer, POINTER(ArrayType))
        # >>> a = numpy.frombuffer(pa.contents, dtype=c_int16)
        # >>> a
        # array([1, 2, 3, ..., 0, 0, 0], dtype=int16)
        # we need a structure to hold our out keys and out n buffer
        out_keys = array_buffer_int32_bit(Get_class_keys, out_keys)
        out_n = array_buffer_int32_bit(Get_class_keys, out_n)
        answer = realm_ffi.realm_get_class_keys(
            c_void_p(self.handle), out_keys, 10, out_n
        )
        print(answer)

        #         /**
        #  * Find a by the name of @a name.
        #  *
        #  * @param name The name of the class.
        #  * @param out_found Set to true if the class was found and no error occurred.
        #  *                  Otherwise, false. May not be NULL.
        #  * @param out_class_info A pointer to a `realm_class_info_t` that will be
        #  *                       populated with information about the class. May be
        #  *                       NULL.
        #  * @return True if no exception occurred.
        #  */
        # RLM_API bool realm_find_class(const realm_t*, const char* name, bool* out_found, realm_class_info_t* out_class_info);

    def realm_find_class(self):
        info = Class_Info()
        name = info.name
        out_info = []
        found = bool()
        out = array_buffer_string(Realm_Find_Class, out_info)

        realm_ffi.realm_find_class.restype = c_bool
        answer = realm_ffi.realm_find_class(c_void_p(self.handle), name, found, out)
        print(answer)

    #     /**
    #  * Get the list of properties for the class with this @a key.
    #  * In case of errors this function will return false (errors to be fetched via `realm_get_last_error()`).
    #  * If data is not copied the function will return true and set  `out_n` with the capacity needed.
    #  * Data is only copied if the input array has enough capacity, otherwise the needed  array capacity will be set.
    #  *
    #  * @param out_properties  A pointer to an array of `realm_property_info_t`, which
    #  *                       will be populated with the information about the
    #  *                       properties.  Array may be NULL, in this case no data will be copied and `out_n` set if not
    #  * NULL.
    #  * @param max The maximum number of entries to write to `out_properties`.
    #  * @param out_n The actual number of properties written to `out_properties`.
    #  * @return True if no exception occurred.
    #  */
    # RLM_API bool realm_get_class_properties(const realm_t*, realm_class_key_t key, realm_property_info_t* out_properties,
    #                                         size_t max, size_t* out_n);
    # def realm_get_class_properties(self):

    # /**
    #  * Create an object in a class without a primary key.
    #  *
    #  * @return A non-NULL pointer if the object was created successfully.
    #  */
    # RLM_API realm_object_t* realm_object_create(realm_t*, realm_class_key_t);
    def realm_object_create(self):
        key = Class_Info().key
        realm_ffi.realm_object_create.restype = c_void_p
        realm_ffi.realm_object_create(c_void_p(self.handle), key)
        print("ok")


config = Configuration(Schema())
realm = Realm(config)
realm.begin_write()
check_error()
realm.realm_is_closed()
check_error()
realm.realm_is_frozen()
check_error()
realm.realm_is_writable()
check_error()
realm.realm_get_num_classes()
check_error()
realm.realm_get_class_keys()
check_error()
realm.realm_find_class()  # create buffer for out_class_info and out_found
check_error()

check_error()
