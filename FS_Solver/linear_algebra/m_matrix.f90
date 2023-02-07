! Description:
! Definition of a matrix.
module m_matrix
    implicit none
    
    private
    public t_matrix, new_matrix
    
    type t_matrix
        integer           :: n_rows   ! number of rows
        integer           :: n_cols   ! number of columns
        real, allocatable :: at(:, :) ! values
    contains
        procedure :: T
        final     :: destructor
    end type
    
    interface new_matrix
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Matrix constructor.
    type(t_matrix) function constructor(n_rows, n_cols) result(this)
        integer, intent(in) :: n_rows ! number of rows
        integer, intent(in) :: n_cols ! number of columns
        this%n_rows = n_rows
        this%n_cols = n_cols
        allocate(this%at(this%n_rows, this%n_cols), source=0.0)
    end function
    
    ! Description:
    ! Matrix destructor.
    subroutine destructor(this)
        type(t_matrix), intent(inout) :: this
        if (allocated(this%at)) deallocate(this%at)
    end subroutine
    
    ! Description:
    ! Transposes the matrix.
    subroutine T(this)
        class(t_matrix), intent(inout) :: this
        real, allocatable :: new_at(:, :)
        
        ! allocate new array
        allocate(new_at(this%n_cols, this%n_rows))
        
        ! transpose
        new_at(:, :) = transpose(this%at(:, :))
        
        ! swap old by new array
        call move_alloc(new_at, this%at) ! new_at is deallocated
        
        ! update matrix shape
        this%n_rows = size(this%at, dim=1)
        this%n_cols = size(this%at, dim=2)
    end subroutine
    
end module
