! Description:
! Definition of a sparse matrix. Matrix has two storage modes:
! * In COO mode, the coordinate storage format is used. In this mode, the
!   matrix can grow in size dynamically and new elements can be added to the
!   matrix. This is the initial mode.
! * In CSR mode, the compressed sparse row storage format is used. This more
!   compact mode is used for computational procedures and elements can no
!   longer be added to the matrix.
module m_sparse
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
    type(t_sparse) function constructor(n_rows, n_cols) result(this)
        integer, intent(in) :: n_rows ! number of rows
        integer, intent(in) :: n_cols ! number of columns
        this%mode   = COO
        this%size   = 1
        this%n_rows = n_rows
        this%n_cols = n_cols
        this%n_nzrs = 0
        allocate(this%row(this%size), source=0  )
        allocate(this%col(this%size), source=0  )
        allocate(this%val(this%size), source=0.0)
    end function
    
    ! Description:
    ! Sparse matrix destructor.
    subroutine destructor(this)
        type(t_sparse), intent(inout) :: this
        if (allocated(this%row)) deallocate(this%row)
        if (allocated(this%col)) deallocate(this%col)
        if (allocated(this%val)) deallocate(this%val)
    end subroutine
    
    ! Description:
    ! Adds the specified element to the matrix.
    subroutine add(this, i, j, v)
        class(t_sparse), intent(inout) :: this ! sparse matrix
        integer,         intent(in)    :: i    ! row index of the element to add
        integer,         intent(in)    :: j    ! column index of the element to add
        real,            intent(in)    :: v    ! value of the element to add
        
        ! check for errors
        if (this%mode /= COO) error stop ERROR_COO_FORMAT_REQUIRED_FOR_SPARSE_MATRIX_OPERATION
        if (i < 1 .or. j < 1 .or. i > this%n_rows .or. j > this%n_cols) error stop ERROR_INDEX_OUT_OF_RANGE_DURING_SPARSE_MATRIX_OPERATION
        
        ! allocate more storage if required
        if (this%n_nzrs == this%size) call resize(this, this%size*2)
        
        ! append new element
        this%row(this%n_nzrs + 1) = i
        this%col(this%n_nzrs + 1) = j
        this%val(this%n_nzrs + 1) = v
        this%n_nzrs = this%n_nzrs + 1
    end subroutine
    
    ! Description:
    ! Converts internal matrix storage from COO to CSR format.
    subroutine to_csr(this)
        class(t_sparse), intent(inout) :: this
        integer, allocatable :: new_row(:)
        integer :: i
        
        ! check for errors
        if (this%mode /= COO) error stop ERROR_COO_FORMAT_REQUIRED_FOR_SPARSE_MATRIX_OPERATION
        
        ! sort arrays and deallocate excess storage
        call sort_and_collapse(this)
        
        ! compute new array
        allocate(new_row(this%n_rows + 1), source=0)                                           ! allocate storage
        do i = 1, this%n_nzrs; new_row(this%row(i) + 1) = new_row(this%row(i) + 1) + 1; end do ! count number of non-zeros per row
        do i = 1, this%n_rows; new_row(i + 1) = new_row(i + 1) + new_row(i); end do            ! cumulative sum per row
        new_row = new_row + 1                                                                  ! get 1-based indices
        
        ! swap old by new array
        call move_alloc(new_row, this%row) ! new_row is deallocated
        
        ! update mode flag and size info
        this%mode = CSR
        this%size = -1
    end subroutine
    
    ! Description:
    ! Resize storage arrays without losing stored data.
    subroutine resize(sparse_matrix, new_size)
        type(t_sparse), intent(inout) :: sparse_matrix ! matrix to resize
        integer,        intent(in)    :: new_size      ! new storage size
        integer, allocatable :: new_row(:) ! new arrays...
        integer, allocatable :: new_col(:)
        real,    allocatable :: new_val(:)
        
        ! check for errors
        if (sparse_matrix%mode /= COO) error stop ERROR_COO_FORMAT_REQUIRED_FOR_SPARSE_MATRIX_OPERATION
        
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
    end subroutine
    
    ! Description:
    ! Sort storage arrays and deallocate excess storage.
    subroutine sort_and_collapse(sparse_matrix)
        type(t_sparse), intent(inout) :: sparse_matrix ! matrix to update
        integer :: n_rep ! number of repeated matrix entries
        integer :: i, j  ! loop counters
        integer :: i_min ! index of minimal matrix entry
        integer :: itemp ! integer temp variable
        real    :: rtemp ! real temp variable
        
        ! check for errors
        if (sparse_matrix%mode /= COO) error stop ERROR_COO_FORMAT_REQUIRED_FOR_SPARSE_MATRIX_OPERATION
        
        ! add repeated matrix entries
        n_rep = 0
        do i = 1, sparse_matrix%n_nzrs
            if (sparse_matrix%row(i) > 0) then
                do j = i + 1, sparse_matrix%n_nzrs
                    if (sparse_matrix%row(j) > 0) then
                        if (sparse_matrix%row(i) == sparse_matrix%row(j) .and. sparse_matrix%col(i) == sparse_matrix%col(j)) then
                            sparse_matrix%val(i) = sparse_matrix%val(i) + sparse_matrix%val(j)
                            sparse_matrix%row(j) = 0
                            sparse_matrix%col(j) = 0
                            sparse_matrix%val(j) = 0.0
                            n_rep = n_rep + 1
                        end if
                    end if
                end do
            end if
        end do
        
        ! sort entries (using selection sort)
        do i = 1, sparse_matrix%n_nzrs
            i_min = i
            do j = i + 1, sparse_matrix%n_nzrs
                if (sparse_matrix%row(j) > 0) then
                    if (sparse_matrix%row(i_min) == 0 .or. sparse_matrix%row(j) < sparse_matrix%row(i_min) .or. (sparse_matrix%row(j) == sparse_matrix%row(i_min) .and. sparse_matrix%col(j) < sparse_matrix%col(i_min))) then
                        i_min = j
                    end if
                end if
            end do
            if (i_min /= i) then
                itemp = sparse_matrix%row(i_min); sparse_matrix%row(i_min) = sparse_matrix%row(i); sparse_matrix%row(i) = itemp ! swap row
                itemp = sparse_matrix%col(i_min); sparse_matrix%col(i_min) = sparse_matrix%col(i); sparse_matrix%col(i) = itemp ! swap col
                rtemp = sparse_matrix%val(i_min); sparse_matrix%val(i_min) = sparse_matrix%val(i); sparse_matrix%val(i) = rtemp ! swap val
            end if
        end do
        
        ! update non-zero element count
        sparse_matrix%n_nzrs = sparse_matrix%n_nzrs - n_rep
        
        ! deallocate excess storage
        call resize(sparse_matrix, sparse_matrix%n_nzrs)
    end subroutine
    
end module
