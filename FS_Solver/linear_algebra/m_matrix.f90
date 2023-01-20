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
        final :: destructor
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
    
end module
