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
    type(t_matrix) function constructor(n_rows, n_cols) result(self)
        integer, intent(in) :: n_rows ! number of rows
        integer, intent(in) :: n_cols ! number of columns
        self%n_rows = n_rows
        self%n_cols = n_cols
        allocate(self%at(self%n_rows, self%n_cols), source=0.0)
    end function
    
    ! Description:
    ! Matrix destructor.
    subroutine destructor(self)
        type(t_matrix), intent(inout) :: self
        if (allocated(self%at)) deallocate(self%at)
    end subroutine
    
    ! Description:
    ! Transposes the matrix.
    subroutine T(self)
        class(t_matrix), intent(inout) :: self
        real, allocatable :: new_at(:, :)
        
        ! allocate new array
        allocate(new_at(self%n_cols, self%n_rows))
        
        ! transpose
        new_at(:, :) = transpose(self%at(:, :))
        
        ! swap old by new array
        call move_alloc(new_at, self%at) ! new_at is deallocated
        
        ! update matrix shape
        self%n_rows = size(self%at, dim=1)
        self%n_cols = size(self%at, dim=2)
    end subroutine
    
end module
