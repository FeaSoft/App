! Description:
! Definition of a sparse matrix. Matrix has two storage modes:
! * In COO mode, the coordinate storage format is used. In self mode, the
!   matrix can grow in size dynamically and new elements can be added to the
!   matrix. This is the initial mode.
! * In CSR mode, the compressed sparse row storage format is used. This more
!   compact mode is used for computational procedures and elements can no
!   longer be added to the matrix.
module m_sparse
    use iso_c_binding
    use mkl_spblas
    implicit none
    
    private
    public t_sparse, new_sparse
    
    ! sparse matrix modes
    integer, parameter :: COO = 31, & ! coordinate storage format
                          CSR = 32    ! compressed sparse row storage format
    
    ! error messages
    character(*), parameter :: ERROR_COO_FORMAT_REQUIRED_FOR_SPARSE_MATRIX_OPERATION   = 'Error: COO format required for sparse matrix operation',   &
                               ERROR_CSR_FORMAT_REQUIRED_FOR_SPARSE_MATRIX_OPERATION   = 'Error: CSR format required for sparse matrix operation',   &
                               ERROR_INDEX_OUT_OF_RANGE_DURING_SPARSE_MATRIX_OPERATION = 'Error: index out of range during sparse matrix operation'
    
    type t_sparse
        integer              :: mode   ! sparse matrix mode (COO or CSR)
        integer              :: size   ! current size of storage arrays
        integer              :: n_rows ! number of rows
        integer              :: n_cols ! number of columns
        integer              :: n_nzrs ! number of non-zero elements
        integer, allocatable :: row(:) ! in COO mode: row index of the i-th non-zero element | in CSR mode: indices of first non-zero elements in row
        integer, allocatable :: col(:) ! column index of the i-th non-zero element
        real,    allocatable :: val(:) ! values of the non-zero elements
    contains
        procedure :: add, to_csr
        final     :: destructor
    end type
    
    interface new_sparse
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Sparse matrix constructor.
    type(t_sparse) function constructor(n_rows, n_cols) result(self)
        integer, intent(in) :: n_rows ! number of rows
        integer, intent(in) :: n_cols ! number of columns
        self%mode   = COO
        self%size   = 1
        self%n_rows = n_rows
        self%n_cols = n_cols
        self%n_nzrs = 0
        allocate(self%row(self%size), source=0  )
        allocate(self%col(self%size), source=0  )
        allocate(self%val(self%size), source=0.0)
    end function
    
    ! Description:
    ! Sparse matrix destructor.
    subroutine destructor(self)
        type(t_sparse), intent(inout) :: self
        if (allocated(self%row)) deallocate(self%row)
        if (allocated(self%col)) deallocate(self%col)
        if (allocated(self%val)) deallocate(self%val)
    end subroutine
    
    ! Description:
    ! Adds the specified element to the matrix.
    subroutine add(self, i, j, v)
        class(t_sparse), intent(inout) :: self ! sparse matrix
        integer,         intent(in)    :: i    ! row index of the element to add
        integer,         intent(in)    :: j    ! column index of the element to add
        real,            intent(in)    :: v    ! value of the element to add
        
        ! check for errors
        if (self%mode /= COO) error stop ERROR_COO_FORMAT_REQUIRED_FOR_SPARSE_MATRIX_OPERATION
        if (i < 1 .or. j < 1 .or. i > self%n_rows .or. j > self%n_cols) error stop ERROR_INDEX_OUT_OF_RANGE_DURING_SPARSE_MATRIX_OPERATION
        
        ! check for v = 0.0
        if (v /= 0.0) then
            
            ! allocate more storage if required
            if (self%n_nzrs == self%size) call resize(self, self%size*2)
            
            ! append new element
            self%row(self%n_nzrs + 1) = i
            self%col(self%n_nzrs + 1) = j
            self%val(self%n_nzrs + 1) = v
            self%n_nzrs = self%n_nzrs + 1
            
        end if
    end subroutine
    
    ! Description:
    ! Resize storage arrays without losing stored data.
    subroutine resize(sparse_matrix, new_size)
        type(t_sparse), intent(inout) :: sparse_matrix ! matrix to resize
        integer,        intent(in)    :: new_size      ! new storage size
        integer,        allocatable   :: new_row(:)    ! new arrays...
        integer,        allocatable   :: new_col(:)
        real,           allocatable   :: new_val(:)
        
        ! check for errors
        if (sparse_matrix%mode /= COO) error stop ERROR_COO_FORMAT_REQUIRED_FOR_SPARSE_MATRIX_OPERATION
        
        if (new_size /= sparse_matrix%size) then
        
            ! allocate new arrays
            allocate(new_row(new_size), source=0  )
            allocate(new_col(new_size), source=0  )
            allocate(new_val(new_size), source=0.0)
        
            ! copy old values to new arrays
            if (new_size > sparse_matrix%size) then
                new_row(1:sparse_matrix%size) = sparse_matrix%row
                new_col(1:sparse_matrix%size) = sparse_matrix%col
                new_val(1:sparse_matrix%size) = sparse_matrix%val
            else
                new_row = sparse_matrix%row(1:new_size)
                new_col = sparse_matrix%col(1:new_size)
                new_val = sparse_matrix%val(1:new_size)
            end if
        
            ! swap old by new arrays
            call move_alloc(new_row, sparse_matrix%row) ! new_row is deallocated
            call move_alloc(new_col, sparse_matrix%col) ! new_col is deallocated
            call move_alloc(new_val, sparse_matrix%val) ! new_val is deallocated
        
            ! update size info
            sparse_matrix%size = new_size
        
        end if
    end subroutine
    
    ! Description:
    ! Converts internal matrix storage from COO to CSR format.
    subroutine to_csr(self)
        class(t_sparse), intent(inout) :: self
        
        ! helper variables
        type(sparse_matrix_t)     :: handle_COO, handle_CSR
        integer                   :: status, indexing, n_rows, n_cols
        type(c_ptr)               :: row_start_c, row_end_c, col_c, val_c
        integer, pointer          :: row_start_f(:), row_end_f(:), col_f(:)
        real,    pointer          :: val_f(:)
        integer, allocatable      :: new_row(:), new_col(:)
        real,    allocatable      :: new_val(:)
        
        ! create COO handle
        status = mkl_sparse_d_create_coo(handle_COO, SPARSE_INDEX_BASE_ONE, self%n_rows, self%n_cols, self%n_nzrs, self%row, self%col, self%val)
        if (status /= SPARSE_STATUS_SUCCESS) error stop 'Error: failure to create MKL handle'
        
        ! convert from COO to CSR
        status = mkl_sparse_convert_csr(handle_COO, SPARSE_OPERATION_NON_TRANSPOSE, handle_CSR)
        if (status /= SPARSE_STATUS_SUCCESS) error stop 'Error: failure to convert COO to CSR'
        
        ! export CSR
        status = mkl_sparse_d_export_csr(handle_CSR, indexing, n_rows, n_cols, row_start_c, row_end_c, col_c, val_c)
        if (status /= SPARSE_STATUS_SUCCESS) error stop 'Error: failure to export MKL handle'
        
        ! convert C pointers to Fortran pointers
        call c_f_pointer(row_start_c, row_start_f, [n_rows]               )
        call c_f_pointer(row_end_c,   row_end_f,   [n_rows]               )
        call c_f_pointer(col_c,       col_f,       [row_end_f(n_rows) - 1])
        call c_f_pointer(val_c,       val_f,       [row_end_f(n_rows) - 1])
        
        ! update number of non-zero elements
        self%n_nzrs = row_end_f(n_rows) - 1
        
        ! create new_row
        allocate(new_row(n_rows + 1))
        new_row(1 : n_rows) = row_start_f(:)
        new_row(n_rows + 1) = row_end_f(n_rows)
        
        ! create new_col
        allocate(new_col(self%n_nzrs))
        new_col(:) = col_f(:)
        
        ! create new_val
        allocate(new_val(self%n_nzrs))
        new_val(:) = val_f(:)
        
        ! swap old by new arrays
        call move_alloc(new_row, self%row) ! new_row is deallocated
        call move_alloc(new_col, self%col) ! new_col is deallocated
        call move_alloc(new_val, self%val) ! new_val is deallocated
        
        ! destroy MKL handles
        status = mkl_sparse_destroy(handle_COO); if (status /= SPARSE_STATUS_SUCCESS) error stop 'Error: failure to destroy MKL handle'
        status = mkl_sparse_destroy(handle_CSR); if (status /= SPARSE_STATUS_SUCCESS) error stop 'Error: failure to destroy MKL handle'
    end subroutine
    
end module
